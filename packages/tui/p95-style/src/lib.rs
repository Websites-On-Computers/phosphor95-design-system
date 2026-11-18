//! # p95-style — Phosphor95 for terminal UIs
//!
//! Win95 structure on a green phosphor CRT, for the terminal. The palettes are generated from
//! the design tokens (`tokens/` in the design-system repo); everything else follows the specs in
//! `components/` and `foundations/`.
//!
//! ```
//! use p95_style::{Env, Theme};
//!
//! // Reads NO_COLOR, COLORTERM, TERM, the locale, and the P95_* switches.
//! let theme = Theme::from_env(&Env::detect());
//! assert!(!theme.palette.name.is_empty());
//! ```
//!
//! Layers:
//! * [`Palette`]: every semantic and component colour of a theme. Each colour is a [`Swatch`]
//!   that carries its truecolor RGB, nearest xterm-256 index and theme ANSI-16 index.
//! * [`Env`] / [`ColorDepth`]: what the terminal can do and what the user asked for.
//! * [`glyphs`]: ASCII-safe / Unicode / Nerd Font glyph tiers, including bevel border sets.
//! * `style` (feature `ratatui`): semantic `Style`s and widget bundles for ratatui.
//!
//! Rules this crate encodes: status always carries a 6-character text tag; selection is inverse
//! video; the focused pane gets a double border (the only depth cue left in mono); mono output
//! uses bold/dim/reverse only.

mod depth;
pub mod glyphs;
pub mod operator;
mod palette;
#[cfg(feature = "ratatui")]
pub mod style;

pub use depth::{ColorDepth, Env};
pub use glyphs::Glyphs;
pub use palette::{duration, Palette, AMBER, GREEN, HC, THEMES, WHITE};
#[cfg(feature = "ratatui")]
pub use style::Theme;

/// One palette colour at every colour depth.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Swatch {
    /// Truecolor red, green, blue.
    pub r: u8,
    pub g: u8,
    pub b: u8,
    /// Nearest xterm-256 colour (16–255; OKLab distance).
    pub x256: u8,
    /// Nearest entry (0–15) in this theme's own ANSI-16 set, i.e. what the colour becomes when
    /// the user's terminal runs the matching Phosphor95 scheme and only 16 colours are available.
    pub ansi: u8,
}

impl Swatch {
    /// Build a swatch (used by the generated palettes).
    pub const fn new(r: u8, g: u8, b: u8, x256: u8, ansi: u8) -> Self {
        Self { r, g, b, x256, ansi }
    }
    /// `#rrggbb`.
    pub fn hex(&self) -> String {
        format!("#{:02x}{:02x}{:02x}", self.r, self.g, self.b)
    }
    /// Linear-light floats for GPU renderers (sRGB decoded), e.g. terminal01's HUD.
    pub fn linear(&self) -> [f32; 3] {
        fn lin(c: u8) -> f32 {
            let c = c as f32 / 255.0;
            if c <= 0.04045 { c / 12.92 } else { ((c + 0.055) / 1.055).powf(2.4) }
        }
        [lin(self.r), lin(self.g), lin(self.b)]
    }
}

/// Status levels. Each has a fixed-width (6 char) tag so log columns line up.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Level {
    Ok,
    Info,
    Warn,
    Error,
    /// In progress / unknown yet.
    Pending,
}

impl Level {
    /// `[ OK ]`, `[INFO]`, `[WARN]`, `[ERR ]`, `[ .. ]`.
    pub const fn tag(self) -> &'static str {
        match self {
            Level::Ok => "[ OK ]",
            Level::Info => "[INFO]",
            Level::Warn => "[WARN]",
            Level::Error => "[ERR ]",
            Level::Pending => "[ .. ]",
        }
    }
    /// The level's foreground swatch in `p` (`status.*.fg`; pending uses `text.secondary`).
    pub const fn fg(self, p: &Palette) -> Swatch {
        match self {
            Level::Ok => p.status_ok_fg,
            Level::Info => p.status_info_fg,
            Level::Warn => p.status_warn_fg,
            Level::Error => p.status_error_fg,
            Level::Pending => p.text_secondary,
        }
    }
}

/// Look up a theme by id (`green`, `amber`, `white`, `hc`; also `high-contrast`).
pub fn palette(name: &str) -> Option<&'static Palette> {
    let n = name.trim().to_ascii_lowercase();
    let n = if n == "high-contrast" || n == "highcontrast" { "hc".to_string() } else { n };
    THEMES.iter().copied().find(|p| p.name == n)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn green_is_the_phosphor95_palette() {
        assert_eq!(GREEN.text_primary.hex(), "#33ff66");
        assert_eq!(GREEN.surface_base.hex(), "#020a04");
        assert_eq!(GREEN.status_warn_fg.hex(), "#ffb000");
    }

    #[test]
    fn amber_warn_is_not_the_text_colour() {
        assert_ne!(AMBER.status_warn_fg, AMBER.text_primary);
    }

    #[test]
    fn tags_are_six_wide() {
        for l in [Level::Ok, Level::Info, Level::Warn, Level::Error, Level::Pending] {
            assert_eq!(l.tag().chars().count(), 6);
        }
    }

    #[test]
    fn lookup() {
        assert_eq!(palette("AMBER").unwrap().name, "amber");
        assert_eq!(palette("high-contrast").unwrap().name, "hc");
        assert!(palette("purple").is_none());
    }

    #[test]
    fn x256_and_ansi_in_range() {
        for p in THEMES {
            let s = p.text_primary;
            assert!(s.x256 >= 16 && s.ansi < 16, "{}", p.name);
        }
    }
}
