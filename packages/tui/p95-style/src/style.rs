//! ratatui styles and widget bundles (feature `ratatui`).
//!
//! Colour policy by depth:
//! * TrueColor / Ansi256: everything is painted, including panel backgrounds (`surface.*`).
//! * Ansi16: foregrounds plus "meaningful" backgrounds (selection, title bars, key caps, status
//!   tints). Surface backgrounds are left to the terminal, which runs the Phosphor95 scheme.
//! * Mono: no colour at all. Meaning moves to modifiers: selection = REVERSED, hot = BOLD,
//!   secondary/disabled = DIM, links = UNDERLINED, and the focused pane gets a double border.

use ratatui::buffer::Buffer;
use ratatui::layout::Rect;
use ratatui::style::{Color, Modifier, Style};
use ratatui::symbols::border;
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Tabs, Widget};

use crate::glyphs::{BorderGlyphs, Tier};
use crate::{palette, ColorDepth, Env, Glyphs, Level, Palette, Swatch, GREEN};

/// A Phosphor95 theme resolved for one terminal.
#[derive(Debug, Clone, Copy)]
pub struct Theme {
    pub palette: &'static Palette,
    pub depth: ColorDepth,
    pub glyphs: &'static Glyphs,
    pub reduced_motion: bool,
}

#[derive(Clone, Copy, PartialEq, Eq)]
enum Bg {
    /// Panel / page surfaces: painted only at 256 colours and up.
    Surface,
    /// Carries meaning (selection, title bar, key cap, status tint): painted whenever there's colour.
    Meaning,
}

impl Theme {
    /// Theme from the environment: `P95_THEME` (default green), detected depth and glyph tier.
    pub fn from_env(env: &Env) -> Self {
        let p = env.theme.as_deref().and_then(palette).unwrap_or(&GREEN);
        Self::new(p, env)
    }

    pub fn new(palette: &'static Palette, env: &Env) -> Self {
        Theme { palette, depth: env.depth, glyphs: Glyphs::for_env(env), reduced_motion: env.reduced_motion }
    }

    /// Same theme, different depth (e.g. to preview fallbacks).
    pub fn with_depth(mut self, depth: ColorDepth) -> Self {
        self.depth = depth;
        self
    }

    /// A swatch at this theme's depth (`None` in mono).
    pub fn color(&self, s: Swatch) -> Option<Color> {
        match self.depth {
            ColorDepth::TrueColor => Some(Color::Rgb(s.r, s.g, s.b)),
            ColorDepth::Ansi256 => Some(Color::Indexed(s.x256)),
            ColorDepth::Ansi16 => Some(Color::Indexed(s.ansi)),
            ColorDepth::Mono => None,
        }
    }

    fn paint(&self, fg: Option<Swatch>, bg: Option<(Swatch, Bg)>, mono: Modifier) -> Style {
        if self.depth == ColorDepth::Mono {
            return Style::default().add_modifier(mono);
        }
        let mut s = Style::default();
        if let Some(c) = fg.and_then(|f| self.color(f)) {
            s = s.fg(c);
        }
        if let Some((b, kind)) = bg {
            if kind == Bg::Meaning || self.depth >= ColorDepth::Ansi256 {
                if let Some(c) = self.color(b) {
                    s = s.bg(c);
                }
            }
        }
        s
    }

    fn mono(&self) -> bool {
        self.depth == ColorDepth::Mono
    }

    // ------------------------------------------------------------- semantic
    /// Page background + body text (`surface.base`, `text.primary`).
    pub fn base(&self) -> Style {
        self.paint(Some(self.palette.text_primary), Some((self.palette.surface_base, Bg::Surface)), Modifier::empty())
    }
    /// Panel / window face (`surface.face`).
    pub fn face(&self) -> Style {
        self.paint(Some(self.palette.text_primary), Some((self.palette.surface_face, Bg::Surface)), Modifier::empty())
    }
    pub fn text(&self) -> Style {
        self.paint(Some(self.palette.text_primary), None, Modifier::empty())
    }
    /// Hints, captions, placeholders (`text.secondary`, ≥ 4.5:1).
    pub fn secondary(&self) -> Style {
        self.paint(Some(self.palette.text_secondary), None, Modifier::DIM)
    }
    /// Hover / focus / headings: glow means hot (`text.hot`).
    pub fn hot(&self) -> Style {
        self.paint(Some(self.palette.text_hot), None, Modifier::BOLD)
    }
    /// Disabled controls only (`text.disabled`).
    pub fn disabled(&self) -> Style {
        self.paint(Some(self.palette.text_disabled), None, Modifier::DIM)
    }
    pub fn link(&self) -> Style {
        self.paint(Some(self.palette.text_link), None, Modifier::empty()).add_modifier(Modifier::UNDERLINED)
    }
    /// Inverted selection (`select.bg` / `select.fg`).
    pub fn selected(&self) -> Style {
        self.paint(Some(self.palette.select_fg), Some((self.palette.select_bg, Bg::Meaning)), Modifier::REVERSED)
    }
    /// Selection in an unfocused list.
    pub fn selected_inactive(&self) -> Style {
        self.paint(Some(self.palette.select_inactive_fg), Some((self.palette.select_inactive_bg, Bg::Meaning)), Modifier::UNDERLINED)
    }
    pub fn title_active(&self) -> Style {
        self.paint(Some(self.palette.title_active_fg), Some((self.palette.title_active_bg, Bg::Meaning)), Modifier::REVERSED | Modifier::BOLD)
    }
    pub fn title_inactive(&self) -> Style {
        self.paint(Some(self.palette.title_inactive_fg), Some((self.palette.title_inactive_bg, Bg::Surface)), Modifier::DIM)
    }
    /// Border colour: `border.strong` for the focused pane, `border.default` otherwise.
    pub fn border(&self, focused: bool) -> Style {
        let s = if focused { self.palette.border_strong } else { self.palette.border_default };
        self.paint(Some(s), None, if focused { Modifier::BOLD } else { Modifier::empty() })
    }
    /// Status text (`status.*.fg`).
    pub fn status(&self, level: Level) -> Style {
        let m = if matches!(level, Level::Warn | Level::Error) { Modifier::BOLD } else { Modifier::empty() };
        self.paint(Some(level.fg(self.palette)), None, m)
    }
    /// Key cap in a hint bar (`statusbar.key-*`).
    pub fn key(&self) -> Style {
        self.paint(Some(self.palette.statusbar_key_fg), Some((self.palette.statusbar_key_bg, Bg::Meaning)), Modifier::REVERSED)
    }
    pub fn statusbar(&self) -> Style {
        self.paint(Some(self.palette.statusbar_fg), Some((self.palette.statusbar_bg, Bg::Surface)), Modifier::empty())
    }
    /// Sunken field well (`field.bg` / `field.text`).
    pub fn field(&self) -> Style {
        self.paint(Some(self.palette.field_text), Some((self.palette.field_bg, Bg::Surface)), Modifier::UNDERLINED)
    }
    pub fn progress_fill(&self) -> Style {
        self.paint(Some(self.palette.progress_fill), None, Modifier::empty())
    }
    pub fn progress_track(&self) -> Style {
        self.paint(Some(self.palette.progress_track), None, Modifier::DIM)
    }
    pub fn table_header(&self) -> Style {
        self.paint(Some(self.palette.list_header_fg), Some((self.palette.list_header_bg, Bg::Surface)), Modifier::BOLD)
    }
    pub fn diff_added(&self) -> Style {
        self.paint(Some(self.palette.diff_added_fg), Some((self.palette.diff_added_bg, Bg::Surface)), Modifier::empty())
    }
    pub fn diff_removed(&self) -> Style {
        self.paint(Some(self.palette.diff_removed_fg), Some((self.palette.diff_removed_bg, Bg::Surface)), Modifier::DIM)
    }

    // -------------------------------------------------------------- borders
    fn set(b: &BorderGlyphs) -> border::Set<'static> {
        border::Set {
            top_left: b.top_left,
            top_right: b.top_right,
            bottom_left: b.bottom_left,
            bottom_right: b.bottom_right,
            vertical_left: b.vertical,
            vertical_right: b.vertical,
            horizontal_top: b.horizontal,
            horizontal_bottom: b.horizontal,
        }
    }

    /// A panel / group box. The focused one gets the double border.
    pub fn panel(&self, title: &str, focused: bool) -> Block<'static> {
        let g = if focused { &self.glyphs.focused } else { &self.glyphs.panel };
        let mut b = Block::default().borders(Borders::ALL).border_set(Self::set(g)).border_style(self.border(focused)).style(self.face());
        if !title.is_empty() {
            let t = format!(" {} ", title.to_uppercase());
            b = b.title(Line::from(Span::styled(t, if focused { self.hot() } else { self.text() })));
        }
        b
    }

    /// A Win95 window: active = double frame with the title inverted in the top edge and the
    /// `[_][□][x]` controls at its right; inactive = single frame, `title.inactive.fg` title.
    pub fn window(&self, title: &str, active: bool) -> Block<'static> {
        let g = if active { &self.glyphs.focused } else { &self.glyphs.panel };
        let t = format!(" {} ", title.to_uppercase());
        let max = if self.glyphs.tier == Tier::Ascii { "#" } else { "□" };
        let controls = format!("[_][{max}][x]");
        Block::default()
            .borders(Borders::ALL)
            .border_set(Self::set(g))
            .border_style(self.border(active))
            .style(self.face())
            .title(Line::from(Span::styled(t, if active { self.title_active() } else { self.title_inactive() })))
            .title(Line::from(Span::styled(controls, self.text())).right_aligned())
    }

    // ------------------------------------------------------------- snippets
    /// `[ OK ] message`: the boot / log line.
    pub fn status_line(&self, level: Level, msg: &str) -> Line<'static> {
        Line::from(vec![Span::styled(level.tag(), self.status(level)), Span::raw(" "), Span::styled(msg.to_uppercase(), self.text())])
    }

    /// A push button: `[ Apply ]`; focused = inverted; default = `«[ OK ]»` (ASCII `<[ OK ]>`).
    pub fn button(&self, label: &str, focused: bool, default: bool, disabled: bool) -> Vec<Span<'static>> {
        let ascii = self.glyphs.tier == Tier::Ascii;
        let core = if focused && (ascii || self.mono()) && !default { format!(">{label}<") } else { format!("[ {label} ]") };
        let style = if disabled { self.disabled() } else if focused { self.selected() } else { self.text() };
        let mut v = Vec::new();
        if default {
            v.push(Span::styled(if ascii { "<" } else { "«" }, self.border(true)));
        }
        v.push(Span::styled(core, style));
        if default {
            v.push(Span::styled(if ascii { ">" } else { "»" }, self.border(true)));
        }
        v
    }

    /// `[x] label` / `[ ] label` (Unicode `[■]`).
    pub fn check(&self, label: &str, on: bool, focused: bool) -> Line<'static> {
        let g = if on { self.glyphs.check_on } else { self.glyphs.check_off };
        Line::from(vec![Span::styled(g, self.text()), Span::raw(" "), Span::styled(label.to_string(), if focused { self.selected() } else { self.text() })])
    }

    /// `(●) label` / `( ) label`.
    pub fn radio(&self, label: &str, on: bool, focused: bool) -> Line<'static> {
        let g = if on { self.glyphs.radio_on } else { self.glyphs.radio_off };
        Line::from(vec![Span::styled(g, self.text()), Span::raw(" "), Span::styled(label.to_string(), if focused { self.selected() } else { self.text() })])
    }

    /// `F1 Help  ^Q Quit` with inverted key caps (ASCII: `[F1]Help`).
    pub fn key_hints(&self, hints: &[(&str, &str)]) -> Line<'static> {
        let ascii = self.glyphs.tier == Tier::Ascii && self.mono();
        let mut v = Vec::new();
        for (i, (k, label)) in hints.iter().enumerate() {
            if i > 0 {
                v.push(Span::raw("  "));
            }
            let cap = if ascii { format!("[{k}]") } else { k.to_string() };
            v.push(Span::styled(cap, self.key()));
            v.push(Span::styled(format!(" {}", label.to_uppercase()), self.statusbar()));
        }
        Line::from(v).style(self.statusbar())
    }

    /// Status bar fields separated by `│` (ASCII `|`).
    pub fn status_bar(&self, fields: Vec<Vec<Span<'static>>>) -> Line<'static> {
        let sep = format!(" {} ", self.glyphs.separator);
        let mut v = vec![Span::raw(" ")];
        for (i, f) in fields.into_iter().enumerate() {
            if i > 0 {
                v.push(Span::styled(sep.clone(), self.secondary()));
            }
            v.extend(f);
        }
        Line::from(v).style(self.statusbar())
    }

    /// Whole-cell progress bar: fill in `progress.fill`, empty track in `progress.track`.
    pub fn progress(&self, ratio: f64, width: usize) -> Line<'static> {
        let (fill, track) = self.glyphs.bar_parts(ratio, width);
        Line::from(vec![Span::styled(fill, self.progress_fill()), Span::styled(track, self.progress_track())])
    }

    /// Spinner frame for `tick`, or the static `[ .. ]` tag under reduced motion.
    pub fn spinner(&self, tick: u64) -> Span<'static> {
        if self.reduced_motion {
            Span::styled(Level::Pending.tag(), self.secondary())
        } else {
            Span::styled(self.glyphs.spinner_frame(tick), self.hot())
        }
    }

    /// Tabs with the selected tab inverted.
    pub fn tabs(&self, titles: &[&str], selected: usize) -> Tabs<'static> {
        let titles: Vec<Line<'static>> = titles.iter().map(|t| Line::from(format!(" {t} "))).collect();
        Tabs::new(titles)
            .select(selected)
            .style(self.secondary())
            .highlight_style(self.selected())
            .divider(Span::styled(self.glyphs.separator, self.border(false)))
            .padding("", "")
    }

    /// The highlight marker for lists: `>` when there's no inversion to rely on.
    pub fn highlight_symbol(&self) -> &'static str {
        if self.mono() || self.glyphs.tier == Tier::Ascii { "> " } else { "  " }
    }
}

/// The Operator, drawn with half-blocks (2 pixels per cell vertically): 48 columns x 24 rows.
/// Colours come from `operator.*`, so it recolours with the theme. In mono or the ASCII glyph tier
/// it falls back to a shade ramp (`:-=+#@`), one character per 2x1 pixels (coloured when possible).
pub struct Operator<'a> {
    pub theme: &'a Theme,
}

impl Widget for Operator<'_> {
    fn render(self, area: Rect, buf: &mut Buffer) {
        let t = self.theme;
        let p = t.palette;
        let roles = [None, Some(p.operator_hair), Some(p.operator_shade_1), Some(p.operator_shade_2),
                     Some(p.operator_mid), Some(p.operator_skin), Some(p.operator_light)];
        let px = |x: usize, y: usize| -> usize { (crate::operator::OPERATOR_48[y][x] - b'0') as usize };
        for row in 0..24usize.min(area.height as usize) {
            for col in 0..48usize.min(area.width as usize) {
                let (top, bot) = (px(col, row * 2), px(col, row * 2 + 1));
                let cell = &mut buf[(area.x + col as u16, area.y + row as u16)];
                if t.depth == ColorDepth::Mono || t.glyphs.tier == Tier::Ascii {
                    const SHADE: [&str; 7] = [" ", ":", "-", "=", "+", "#", "@"];
                    let r = top.max(bot);
                    cell.set_symbol(SHADE[r]);
                    if let Some(c) = roles[r].and_then(|s| t.color(s)) {
                        cell.set_fg(c);
                    }
                    continue;
                }
                let (tc, bc) = (roles[top].and_then(|s| t.color(s)), roles[bot].and_then(|s| t.color(s)));
                match (tc, bc) {
                    (Some(a), Some(b)) => { cell.set_symbol("▀").set_fg(a).set_bg(b); }
                    (Some(a), None) => { cell.set_symbol("▀").set_fg(a); }
                    (None, Some(b)) => { cell.set_symbol("▄").set_fg(b); }
                    (None, None) => {}
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{AMBER, HC};

    fn env(depth: ColorDepth, unicode: bool) -> Env {
        Env { depth, unicode, nerd_font: false, reduced_motion: false, theme: None }
    }

    #[test]
    fn truecolor_paints_rgb() {
        let t = Theme::new(&GREEN, &env(ColorDepth::TrueColor, true));
        assert_eq!(t.text().fg, Some(Color::Rgb(0x33, 0xff, 0x66)));
        assert_eq!(t.base().bg, Some(Color::Rgb(0x02, 0x0a, 0x04)));
    }

    #[test]
    fn ansi16_skips_surface_backgrounds_but_keeps_selection() {
        let t = Theme::new(&AMBER, &env(ColorDepth::Ansi16, true));
        assert_eq!(t.face().bg, None);
        assert!(matches!(t.selected().bg, Some(Color::Indexed(i)) if i < 16));
        assert_eq!(t.text().fg, Some(Color::Indexed(AMBER.ansi_green.ansi)));
    }

    #[test]
    fn mono_uses_only_modifiers() {
        let t = Theme::new(&HC, &env(ColorDepth::Mono, false));
        for s in [t.text(), t.selected(), t.hot(), t.secondary(), t.key(), t.title_active(), t.status(Level::Error)] {
            assert_eq!((s.fg, s.bg), (None, None));
        }
        assert!(t.selected().add_modifier.contains(Modifier::REVERSED));
        assert_eq!(t.highlight_symbol(), "> ");
    }

    #[test]
    fn progress_spans_cover_width() {
        for unicode in [true, false] {
            let t = Theme::new(&GREEN, &env(ColorDepth::TrueColor, unicode));
            for r in [0.0, 0.33, 0.62, 1.0] {
                let l = t.progress(r, 24);
                assert_eq!(l.width(), 24, "unicode={unicode} r={r}");
            }
        }
    }

    #[test]
    fn reduced_motion_spinner_is_static() {
        let mut e = env(ColorDepth::TrueColor, true);
        e.reduced_motion = true;
        let t = Theme::new(&GREEN, &e);
        assert_eq!(t.spinner(0).content, t.spinner(7).content);
    }
}
