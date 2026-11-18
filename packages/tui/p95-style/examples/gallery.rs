//! Phosphor95 TUI gallery: every terminal component in one screen.
//!
//!   cargo run --example gallery                       # interactive
//!   cargo run --example gallery -- --snapshot --theme amber --depth 256 --size 100x34
//!
//! Keys: 1-4 theme · d colour depth · a ASCII/Unicode · Tab focus · ←/→ tabs · ↑/↓ list · Space toggle · q quit
//! `--snapshot` renders one frame to an in-memory buffer and prints it as ANSI (for docs/tests).

use std::time::{Duration, Instant};

use p95_style::style::Operator;
use p95_style::{duration, glyphs, palette, ColorDepth, Env, Level, Theme, THEMES};
use ratatui::backend::TestBackend;
use ratatui::buffer::Buffer;
use ratatui::crossterm::event::{self, Event, KeyCode, KeyEventKind};
use ratatui::layout::{Constraint, Layout, Rect};
use ratatui::style::{Color, Modifier};
use ratatui::text::{Line, Span};
use ratatui::widgets::{List, ListItem, ListState, Paragraph, Row, Table};
use ratatui::{Frame, Terminal};

struct App {
    theme: Theme,
    tab: usize,
    focus: usize, // 0 models, 1 options
    list: ListState,
    checks: [bool; 3],
    tick: u64,
    quit: bool,
}

const MODELS: [(&str, Level); 4] =
    [("qwen2.5-7b", Level::Ok), ("llama3-8b", Level::Info), ("claude", Level::Warn), ("phi-3", Level::Error)];
const DEPTHS: [ColorDepth; 4] = [ColorDepth::TrueColor, ColorDepth::Ansi256, ColorDepth::Ansi16, ColorDepth::Mono];

fn depth_name(d: ColorDepth) -> &'static str {
    match d {
        ColorDepth::TrueColor => "TRUECOLOR",
        ColorDepth::Ansi256 => "256",
        ColorDepth::Ansi16 => "16",
        ColorDepth::Mono => "MONO",
    }
}

impl App {
    fn new(theme: Theme) -> Self {
        let mut list = ListState::default();
        list.select(Some(1));
        App { theme, tab: 0, focus: 0, list, checks: [true, false, true], tick: 0, quit: false }
    }

    fn draw(&mut self, f: &mut Frame) {
        let t = self.theme;
        let area = f.area();
        f.render_widget(Paragraph::new("").style(t.base()), area);
        let [menu, body, hints, status] =
            Layout::vertical([Constraint::Length(1), Constraint::Min(10), Constraint::Length(1), Constraint::Length(1)]).areas(area);

        // Menubar
        let mut m = vec![Span::styled(" ", t.face())];
        for (i, item) in ["File", "Edit", "View", "Help"].iter().enumerate() {
            m.push(Span::styled(format!(" {item} "), if i == 2 { t.selected() } else { t.face() }));
        }
        f.render_widget(Paragraph::new(Line::from(m)).style(t.face()), menu);

        // Window
        let win = t.window("SYS.TERMINAL — Properties", true);
        let inner = win.inner(body);
        f.render_widget(win, body);
        let [tabs, content] = Layout::vertical([Constraint::Length(1), Constraint::Min(1)]).areas(inner);
        f.render_widget(t.tabs(&["Components", "Palette", "Operator"], self.tab), tabs);
        match self.tab {
            0 => self.components(f, content),
            1 => self.palette(f, content),
            _ => self.operator(f, content),
        }

        // Key hints and status bar
        f.render_widget(
            Paragraph::new(t.key_hints(&[("1-4", "Theme"), ("D", "Depth"), ("A", "Glyphs"), ("Tab", "Focus"), (if t.glyphs.tier == glyphs::Tier::Ascii { "<>" } else { "←→" }, "Tabs"), ("Q", "Quit")])),
            hints,
        );
        let tier = match t.glyphs.tier { glyphs::Tier::Ascii => "ASCII", glyphs::Tier::Unicode => "UNICODE", glyphs::Tier::NerdFont => "NERD" };
        let fields = vec![
            vec![Span::styled("TERMINAL-01", t.hot())],
            vec![Span::styled(format!("P95 {}", t.palette.name.to_uppercase()), t.text())],
            vec![Span::styled(depth_name(t.depth), t.text())],
            vec![Span::styled(tier, t.text())],
            vec![Span::styled(Level::Warn.tag(), t.status(Level::Warn)), Span::styled(" 95°C", t.text())],
        ];
        f.render_widget(Paragraph::new(t.status_bar(fields)), status);
    }

    fn components(&mut self, f: &mut Frame, area: Rect) {
        let t = self.theme;
        let [left, right] = Layout::horizontal([Constraint::Percentage(48), Constraint::Percentage(52)]).areas(area);
        let [models, options] = Layout::vertical([Constraint::Length(7), Constraint::Min(6)]).areas(left);

        // List (focusable)
        let items: Vec<ListItem> = MODELS
            .iter()
            .map(|(name, lvl)| {
                ListItem::new(Line::from(vec![Span::raw(format!("{name:<14}")), Span::styled(lvl.tag(), t.status(*lvl))]))
            })
            .collect();
        let focused = self.focus == 0;
        let list = List::new(items)
            .block(t.panel("Models", focused))
            .style(t.text())
            .highlight_style(if focused { t.selected() } else { t.selected_inactive() })
            .highlight_symbol(t.highlight_symbol());
        f.render_stateful_widget(list, models, &mut self.list);

        // Options: checkboxes, radios, buttons
        let opt_focus = self.focus == 1;
        let block = t.panel("Options", opt_focus);
        let oi = block.inner(options);
        f.render_widget(block, options);
        let mut lines = vec![
            t.check("Stream tokens", self.checks[0], opt_focus),
            t.check("Log to disk", self.checks[1], false),
            t.check("Wake word", self.checks[2], false),
            Line::from([t.radio("Text", true, false).spans, vec![Span::raw("   ")], t.radio("Voice", false, false).spans].concat()),
            Line::raw(""),
        ];
        let mut buttons = t.button("OK", false, true, false);
        buttons.push(Span::raw(" "));
        buttons.extend(t.button("Cancel", opt_focus, false, false));
        buttons.push(Span::raw(" "));
        buttons.extend(t.button("Apply", false, false, true));
        lines.push(Line::from(buttons));
        f.render_widget(Paragraph::new(lines).style(t.text()), oi);

        // Right column: status, progress, table, log
        let [stat, table, log] = Layout::vertical([Constraint::Length(6), Constraint::Length(6), Constraint::Min(4)]).areas(right);
        let sb = t.panel("Uplink", false);
        let si = sb.inner(stat);
        f.render_widget(sb, stat);
        let w = si.width.saturating_sub(1) as usize;
        let spin = vec![t.spinner(self.tick), Span::styled(" TRANSCRIBING", t.text())];
        f.render_widget(
            Paragraph::new(vec![
                Line::from(vec![Span::styled("UPLINK", t.text()), Span::styled(format!("{:>w$}", "62%", w = w.saturating_sub(6)), t.text())]),
                t.progress(0.62, w),
                Line::from(spin),
                Line::from(vec![Span::styled("Hint: ", t.secondary()), Span::styled("press Space to toggle", t.secondary())]),
            ]),
            si,
        );

        let header = Row::new(["HOST", "CPU", "MEM"]).style(t.table_header());
        let rows = [
            Row::new(["terminal-01", "12%", "540M"]),
            Row::new(["node-01", "38%", "21G"]).style(t.selected()),
            Row::new(["nas", "3%", "2G"]),
        ];
        let tbl = Table::new(rows, [Constraint::Min(12), Constraint::Length(5), Constraint::Length(6)])
            .header(header)
            .block(t.panel("Nodes", false))
            .style(t.text());
        f.render_widget(tbl, table);

        let lb = t.panel("Log", false);
        let li = lb.inner(log);
        f.render_widget(lb, log);
        f.render_widget(
            Paragraph::new(vec![
                t.status_line(Level::Ok, "network up"),
                t.status_line(Level::Info, "whisper base.en loaded"),
                t.status_line(Level::Warn, "cpu 95 °c, throttling"),
                t.status_line(Level::Error, "brain unreachable"),
                t.status_line(Level::Pending, "reconnecting"),
            ]),
            li,
        );
    }

    fn palette(&self, f: &mut Frame, area: Rect) {
        let t = self.theme;
        let p = t.palette;
        let ramp = [p.phosphor_1, p.phosphor_2, p.phosphor_3, p.phosphor_4, p.phosphor_5, p.phosphor_6,
                    p.phosphor_7, p.phosphor_8, p.phosphor_9, p.phosphor_10, p.phosphor_11, p.phosphor_12];
        let chip = |s: p95_style::Swatch| -> Span<'static> {
            match t.color(s) {
                Some(c) => Span::styled("      ", ratatui::style::Style::default().bg(c)),
                None => Span::styled("[mono]", t.secondary()),
            }
        };
        let mut lines = vec![Line::styled(format!("PHOSPHOR RAMP  1 {} 12", t.glyphs.arrow_right), t.hot()), Line::raw("")];
        lines.push(Line::from(ramp.iter().flat_map(|s| [chip(*s), Span::raw(" ")]).collect::<Vec<_>>()));
        lines.push(Line::from(
            (1..=12).map(|i| Span::styled(format!("{i:<7}"), t.secondary())).collect::<Vec<_>>(),
        ));
        lines.push(Line::raw(""));
        lines.push(Line::styled("STATUS", t.hot()));
        for l in [Level::Ok, Level::Info, Level::Warn, Level::Error] {
            let s = l.fg(p);
            lines.push(Line::from(vec![chip(s), Span::raw(" "), Span::styled(l.tag(), t.status(l)), Span::styled(format!(" {}", s.hex()), t.secondary())]));
        }
        lines.push(Line::raw(""));
        lines.push(Line::styled("ANSI-16", t.hot()));
        let ansi = [p.ansi_black, p.ansi_red, p.ansi_green, p.ansi_yellow, p.ansi_blue, p.ansi_magenta, p.ansi_cyan, p.ansi_white,
                    p.ansi_bright_black, p.ansi_bright_red, p.ansi_bright_green, p.ansi_bright_yellow,
                    p.ansi_bright_blue, p.ansi_bright_magenta, p.ansi_bright_cyan, p.ansi_bright_white];
        lines.push(Line::from(ansi[..8].iter().flat_map(|s| [chip(*s), Span::raw(" ")]).collect::<Vec<_>>()));
        lines.push(Line::raw(""));
        lines.push(Line::from(ansi[8..].iter().flat_map(|s| [chip(*s), Span::raw(" ")]).collect::<Vec<_>>()));
        f.render_widget(Paragraph::new(lines).style(t.text()), area.inner(ratatui::layout::Margin::new(1, 1)));
    }

    fn operator(&self, f: &mut Frame, area: Rect) {
        let t = self.theme;
        let [art, text] = Layout::horizontal([Constraint::Length(50), Constraint::Min(10)]).areas(area);
        let a = Rect { x: art.x + 1, y: art.y + 1, width: art.width.saturating_sub(1), height: art.height.saturating_sub(1) };
        f.render_widget(Operator { theme: &t }, a);
        f.render_widget(
            Paragraph::new(vec![
                Line::raw(""),
                Line::styled("THE OPERATOR", t.hot()),
                Line::raw(""),
                Line::styled("The lock-screen avatar, 48x48,", t.text()),
                Line::styled("drawn with half-blocks. It", t.text()),
                Line::styled("recolours with the theme.", t.text()),
                Line::raw(""),
                Line::styled("PHOSPHOR95 // DESIGN SYSTEM", t.secondary()),
            ]),
            text,
        );
    }

    fn key(&mut self, code: KeyCode, env: &Env) {
        match code {
            KeyCode::Char('q') | KeyCode::Esc => self.quit = true,
            KeyCode::Char(c @ '1'..='4') => {
                let p = THEMES[(c as u8 - b'1') as usize];
                let depth = self.theme.depth;
                let glyphs = self.theme.glyphs;
                self.theme = Theme::new(p, env).with_depth(depth);
                self.theme.glyphs = glyphs;
            }
            KeyCode::Char('d') => {
                let i = DEPTHS.iter().position(|d| *d == self.theme.depth).unwrap_or(0);
                self.theme.depth = DEPTHS[(i + 1) % DEPTHS.len()];
            }
            KeyCode::Char('a') => {
                self.theme.glyphs = if self.theme.glyphs.tier == glyphs::Tier::Ascii { &glyphs::UNICODE } else { &glyphs::ASCII };
            }
            KeyCode::Tab => self.focus = (self.focus + 1) % 2,
            KeyCode::Left => self.tab = (self.tab + 2) % 3,
            KeyCode::Right => self.tab = (self.tab + 1) % 3,
            KeyCode::Down if self.focus == 0 => self.list.select(Some((self.list.selected().unwrap_or(0) + 1).min(MODELS.len() - 1))),
            KeyCode::Up if self.focus == 0 => self.list.select(Some(self.list.selected().unwrap_or(0).saturating_sub(1))),
            KeyCode::Char(' ') => self.checks[0] = !self.checks[0],
            _ => {}
        }
    }
}

// ------------------------------------------------------------------ snapshot
fn sgr(c: Color, bg: bool) -> String {
    let base = if bg { 40 } else { 30 };
    match c {
        Color::Reset => format!("{}", if bg { 49 } else { 39 }),
        Color::Rgb(r, g, b) => format!("{};2;{r};{g};{b}", if bg { 48 } else { 38 }),
        Color::Indexed(i) if i < 8 => format!("{}", base + i),
        Color::Indexed(i) if i < 16 => format!("{}", base + 60 + i - 8),
        Color::Indexed(i) => format!("{};5;{i}", if bg { 48 } else { 38 }),
        _ => String::new(),
    }
}

fn print_ansi(buf: &Buffer) {
    let w = buf.area.width as usize;
    let mut out = String::new();
    for (i, cell) in buf.content.iter().enumerate() {
        let mut codes = vec!["0".to_string()];
        let m = cell.modifier;
        if m.contains(Modifier::BOLD) { codes.push("1".into()); }
        if m.contains(Modifier::DIM) { codes.push("2".into()); }
        if m.contains(Modifier::UNDERLINED) { codes.push("4".into()); }
        if m.contains(Modifier::REVERSED) { codes.push("7".into()); }
        for (c, bg) in [(cell.fg, false), (cell.bg, true)] {
            let s = sgr(c, bg);
            if !s.is_empty() { codes.push(s); }
        }
        out.push_str(&format!("\x1b[{}m{}", codes.join(";"), cell.symbol()));
        if (i + 1) % w == 0 { out.push_str("\x1b[0m\n"); }
    }
    print!("{out}");
}

fn main() -> std::io::Result<()> {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let arg = |name: &str| args.iter().position(|a| a == name).and_then(|i| args.get(i + 1)).cloned();
    let mut env = Env::detect();
    if let Some(d) = arg("--depth") {
        env.depth = match d.as_str() { "truecolor" | "24" => ColorDepth::TrueColor, "256" => ColorDepth::Ansi256, "16" => ColorDepth::Ansi16, _ => ColorDepth::Mono };
    }
    if args.iter().any(|a| a == "--ascii") { env.unicode = false; env.nerd_font = false; }
    if args.iter().any(|a| a == "--unicode") { env.unicode = true; }
    let pal = arg("--theme").as_deref().and_then(palette).or(env.theme.as_deref().and_then(palette)).unwrap_or(THEMES[0]);
    let mut app = App::new(Theme::new(pal, &env));
    if let Some(tab) = arg("--tab") { app.tab = tab.parse().unwrap_or(0).min(2); }

    if args.iter().any(|a| a == "--snapshot") {
        let (w, h) = arg("--size").and_then(|s| s.split_once('x').map(|(a, b)| (a.parse().unwrap_or(100), b.parse().unwrap_or(34)))).unwrap_or((100, 34));
        let mut term = Terminal::new(TestBackend::new(w, h)).expect("test backend");
        term.draw(|f| app.draw(f)).expect("draw");
        print_ansi(term.backend().buffer());
        return Ok(());
    }

    let mut terminal = ratatui::init();
    let tick = Duration::from_millis(duration::FAST);
    let mut last = Instant::now();
    let result = (|| -> std::io::Result<()> {
        while !app.quit {
            terminal.draw(|f| app.draw(f))?;
            if event::poll(tick.saturating_sub(last.elapsed()))? {
                if let Event::Key(k) = event::read()? {
                    if k.kind == KeyEventKind::Press { app.key(k.code, &env); }
                }
            }
            if last.elapsed() >= tick { app.tick += 1; last = Instant::now(); }
        }
        Ok(())
    })();
    ratatui::restore();
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn renders_every_theme_depth_and_tab_without_panicking() {
        for p in THEMES {
            for d in DEPTHS {
                for unicode in [true, false] {
                    let env = Env { depth: d, unicode, nerd_font: false, reduced_motion: false, theme: None };
                    let mut app = App::new(Theme::new(p, &env));
                    for tab in 0..3 {
                        app.tab = tab;
                        let mut term = Terminal::new(TestBackend::new(100, 34)).unwrap();
                        term.draw(|f| app.draw(f)).unwrap();
                        let buf = term.backend().buffer();
                        let text: String = buf.content.iter().map(|c| c.symbol()).collect();
                        assert!(text.contains("SYS.TERMINAL"), "{} {:?}", p.name, d);
                        if d == ColorDepth::Mono {
                            assert!(buf.content.iter().all(|c| c.fg == Color::Reset && c.bg == Color::Reset), "mono leaked colour");
                        }
                        if !unicode {
                            // No Unicode-tier glyph may leak into the ASCII tier (content text aside).
                            let leaked: Vec<char> = text.chars().filter(|c| "┌┐└┘─│╔╗╚╝═║█▓▒░▀▄►◄▲▼■●✓✗«»…⠋".contains(*c)).collect();
                            assert!(leaked.is_empty(), "{} {:?} tab {tab}: {:?}", p.name, d, leaked);
                        }
                    }
                }
            }
        }
    }
}
