//! Glyph tiers (foundations/iconography.md): ASCII-safe (tier 1, always works), Unicode (tier 2,
//! default on UTF-8), Nerd Font (tier 3, opt-in with `P95_NERD_FONT=1`). Every app must work on tier 1.

use crate::Env;

/// Box-drawing set for one border style.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct BorderGlyphs {
    pub top_left: &'static str,
    pub top_right: &'static str,
    pub bottom_left: &'static str,
    pub bottom_right: &'static str,
    pub horizontal: &'static str,
    pub vertical: &'static str,
}

/// Every glyph a Phosphor95 TUI draws, for one tier.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Glyphs {
    pub tier: Tier,
    /// Short status icons; the 6-char text tags (`Level::tag`) are always available too.
    pub ok: &'static str,
    pub info: &'static str,
    pub warn: &'static str,
    pub error: &'static str,
    pub check_on: &'static str,
    pub check_off: &'static str,
    pub radio_on: &'static str,
    pub radio_off: &'static str,
    pub arrow_left: &'static str,
    pub arrow_right: &'static str,
    pub arrow_up: &'static str,
    pub arrow_down: &'static str,
    pub tree_open: &'static str,
    pub tree_closed: &'static str,
    pub tree_branch: &'static str,
    pub tree_last: &'static str,
    pub tree_pipe: &'static str,
    pub submenu: &'static str,
    pub separator: &'static str,
    pub cursor: &'static str,
    pub ellipsis: &'static str,
    /// Progress cells, full → empty. Fill with whole cells; partials only for the leading cell.
    pub progress: [&'static str; 4],
    /// Spinner frames, advanced every `duration::FAST` ms. Not drawn under reduced motion.
    pub spinner: &'static [&'static str],
    /// Unfocused panels / group boxes (`border.default`).
    pub panel: BorderGlyphs,
    /// The focused pane or active window (`border.strong` / `border.focus`). In mono this
    /// double border is the only depth cue left, so it must always differ from `panel`.
    pub focused: BorderGlyphs,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Tier {
    Ascii,
    Unicode,
    NerdFont,
}

const ASCII_PANEL: BorderGlyphs = BorderGlyphs { top_left: "+", top_right: "+", bottom_left: "+", bottom_right: "+", horizontal: "-", vertical: "|" };
const ASCII_FOCUSED: BorderGlyphs = BorderGlyphs { top_left: "#", top_right: "#", bottom_left: "#", bottom_right: "#", horizontal: "=", vertical: "|" };
const UNI_PANEL: BorderGlyphs = BorderGlyphs { top_left: "┌", top_right: "┐", bottom_left: "└", bottom_right: "┘", horizontal: "─", vertical: "│" };
const UNI_FOCUSED: BorderGlyphs = BorderGlyphs { top_left: "╔", top_right: "╗", bottom_left: "╚", bottom_right: "╝", horizontal: "═", vertical: "║" };

pub const ASCII: Glyphs = Glyphs {
    tier: Tier::Ascii,
    ok: "+", info: "i", warn: "!", error: "x",
    check_on: "[x]", check_off: "[ ]", radio_on: "(*)", radio_off: "( )",
    arrow_left: "<", arrow_right: ">", arrow_up: "^", arrow_down: "v",
    tree_open: "[-]", tree_closed: "[+]", tree_branch: "|-", tree_last: "`-", tree_pipe: "| ",
    submenu: ">", separator: "|", cursor: "_", ellipsis: "...",
    progress: ["#", "=", "-", "."],
    spinner: &["|", "/", "-", "\\"],
    panel: ASCII_PANEL, focused: ASCII_FOCUSED,
};

pub const UNICODE: Glyphs = Glyphs {
    tier: Tier::Unicode,
    ok: "✓", info: "i", warn: "!", error: "✗",
    check_on: "[■]", check_off: "[ ]", radio_on: "(●)", radio_off: "( )",
    arrow_left: "◄", arrow_right: "►", arrow_up: "▲", arrow_down: "▼",
    tree_open: "▼", tree_closed: "►", tree_branch: "├─", tree_last: "└─", tree_pipe: "│ ",
    submenu: "►", separator: "│", cursor: "█", ellipsis: "…",
    progress: ["█", "▓", "▒", "░"],
    spinner: &["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    panel: UNI_PANEL, focused: UNI_FOCUSED,
};

/// Unicode plus Nerd Font icons (Font Awesome range in Nerd Fonts).
pub const NERD_FONT: Glyphs = Glyphs {
    tier: Tier::NerdFont,
    ok: "\u{f00c}", info: "\u{f05a}", warn: "\u{f071}", error: "\u{f00d}",
    check_on: "\u{f14a}", check_off: "\u{f096}", radio_on: "\u{f192}", radio_off: "\u{f10c}",
    arrow_left: "\u{f060}", arrow_right: "\u{f061}", arrow_up: "\u{f062}", arrow_down: "\u{f063}",
    tree_open: "\u{f07c}", tree_closed: "\u{f07b}",
    submenu: "\u{f054}",
    ..UNICODE
};

impl Glyphs {
    /// The tier the environment allows.
    pub fn for_env(env: &Env) -> &'static Glyphs {
        if env.nerd_font {
            &NERD_FONT
        } else if env.unicode {
            &UNICODE
        } else {
            &ASCII
        }
    }

    /// A whole-cell progress bar of `width` cells for `ratio` (0..=1). The leading cell may use a
    /// partial block; everything after it is the empty glyph.
    pub fn bar(&self, ratio: f64, width: usize) -> String {
        let (fill, track) = self.bar_parts(ratio, width);
        fill + &track
    }

    /// [`Glyphs::bar`] split into the filled part (incl. a partial leading cell) and the empty track.
    pub fn bar_parts(&self, ratio: f64, width: usize) -> (String, String) {
        let exact = ratio.clamp(0.0, 1.0) * width as f64;
        let full = (exact.floor() as usize).min(width);
        let mut fill = self.progress[0].repeat(full);
        let mut empty = width - full;
        if full < width {
            let frac = exact - full as f64;
            if frac >= 1.0 / 3.0 {
                fill.push_str(if frac >= 2.0 / 3.0 { self.progress[1] } else { self.progress[2] });
                empty -= 1;
            }
        }
        (fill, self.progress[3].repeat(empty))
    }

    /// Spinner frame for a monotonically increasing tick.
    pub fn spinner_frame(&self, tick: u64) -> &'static str {
        self.spinner[(tick as usize) % self.spinner.len()]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn bar_widths() {
        for g in [&ASCII, &UNICODE] {
            for r in [0.0, 0.1, 0.5, 0.62, 0.99, 1.0] {
                assert_eq!(g.bar(r, 20).chars().count(), 20, "{:?} {r}", g.tier);
            }
        }
        assert_eq!(UNICODE.bar(1.0, 4), "████");
        assert_eq!(UNICODE.bar(0.0, 4), "░░░░");
        assert_eq!(ASCII.bar(0.5, 4), "##..");
    }

    #[test]
    fn focused_differs_from_panel() {
        for g in [&ASCII, &UNICODE, &NERD_FONT] {
            assert_ne!(g.panel, g.focused);
        }
    }

    #[test]
    fn ascii_tier_is_ascii() {
        let g = ASCII;
        let all = [g.ok, g.info, g.warn, g.error, g.check_on, g.check_off, g.radio_on, g.radio_off, g.arrow_left,
                   g.arrow_right, g.arrow_up, g.arrow_down, g.tree_open, g.tree_closed, g.tree_branch, g.tree_last,
                   g.tree_pipe, g.submenu, g.separator, g.cursor, g.ellipsis];
        assert!(all.iter().chain(g.progress.iter()).chain(g.spinner.iter()).all(|s| s.is_ascii()));
    }
}
