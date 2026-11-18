//! What the terminal can do, and what the user asked for.

/// How many colours we may emit.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum ColorDepth {
    /// No colour escapes at all (`NO_COLOR`, `TERM=dumb`): bold / dim / reverse only.
    Mono,
    /// The terminal's 16 colours. With a Phosphor95 scheme installed these *are* the theme.
    Ansi16,
    /// xterm-256 (nearest match precomputed per swatch).
    Ansi256,
    /// 24-bit RGB.
    TrueColor,
}

/// Detected terminal capabilities and Phosphor95 user switches.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Env {
    pub depth: ColorDepth,
    /// UTF-8 locale and not forced to ASCII: box drawing, blocks, `►`.
    pub unicode: bool,
    /// `P95_NERD_FONT=1`: use Nerd Font icons (tier 3). Off by default.
    pub nerd_font: bool,
    /// `P95_REDUCED_MOTION=1` (or no TTY, decided by the app): no spinners or typing animation.
    pub reduced_motion: bool,
    /// `P95_THEME` (green, amber, white, hc), if set.
    pub theme: Option<String>,
}

fn truthy(v: Option<String>) -> bool {
    matches!(v.as_deref().map(str::trim), Some(s) if !s.is_empty() && s != "0" && !s.eq_ignore_ascii_case("false"))
}

impl Env {
    /// Read the real process environment.
    pub fn detect() -> Self {
        Self::from_vars(|k| std::env::var(k).ok())
    }

    /// Detect from any variable source (handy for tests).
    ///
    /// Precedence for colour depth:
    /// 1. `NO_COLOR` set and non-empty → [`ColorDepth::Mono`] (<https://no-color.org>)
    /// 2. `P95_COLOR` = `truecolor` | `256` | `16` | `mono` (explicit override)
    /// 3. `TERM=dumb` → Mono
    /// 4. `COLORTERM` = `truecolor` | `24bit` → TrueColor
    /// 5. `TERM` contains `256color` (or `direct`/`truecolor`) → Ansi256 (TrueColor for `direct`)
    /// 6. otherwise Ansi16
    pub fn from_vars(get: impl Fn(&str) -> Option<String>) -> Self {
        let term = get("TERM").unwrap_or_default().to_ascii_lowercase();
        let no_color = get("NO_COLOR").is_some_and(|v| !v.is_empty());
        let depth = if no_color {
            ColorDepth::Mono
        } else if let Some(o) = get("P95_COLOR") {
            match o.trim().to_ascii_lowercase().as_str() {
                "truecolor" | "24bit" | "rgb" => ColorDepth::TrueColor,
                "256" | "ansi256" => ColorDepth::Ansi256,
                "16" | "ansi" | "ansi16" => ColorDepth::Ansi16,
                _ => ColorDepth::Mono,
            }
        } else if term == "dumb" {
            ColorDepth::Mono
        } else if matches!(get("COLORTERM").unwrap_or_default().to_ascii_lowercase().as_str(), "truecolor" | "24bit")
            || term.contains("direct")
            || term.contains("truecolor")
        {
            ColorDepth::TrueColor
        } else if term.contains("256color") {
            ColorDepth::Ansi256
        } else {
            ColorDepth::Ansi16
        };

        let locale = ["LC_ALL", "LC_CTYPE", "LANG"].iter().find_map(|k| get(k).filter(|v| !v.is_empty())).unwrap_or_default();
        let utf8 = locale.to_ascii_lowercase().replace('-', "").contains("utf8");
        let unicode = utf8 && !truthy(get("P95_ASCII")) && term != "dumb";

        Env {
            depth,
            unicode,
            nerd_font: unicode && truthy(get("P95_NERD_FONT")),
            reduced_motion: truthy(get("P95_REDUCED_MOTION")),
            theme: get("P95_THEME").filter(|t| !t.trim().is_empty()),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashMap;

    fn env(pairs: &[(&str, &str)]) -> Env {
        let m: HashMap<String, String> = pairs.iter().map(|(k, v)| (k.to_string(), v.to_string())).collect();
        Env::from_vars(|k| m.get(k).cloned())
    }

    #[test]
    fn no_color_wins() {
        assert_eq!(env(&[("NO_COLOR", "1"), ("COLORTERM", "truecolor"), ("P95_COLOR", "256")]).depth, ColorDepth::Mono);
    }
    #[test]
    fn empty_no_color_is_ignored() {
        assert_eq!(env(&[("NO_COLOR", ""), ("COLORTERM", "truecolor")]).depth, ColorDepth::TrueColor);
    }
    #[test]
    fn override_and_term() {
        assert_eq!(env(&[("P95_COLOR", "16"), ("COLORTERM", "truecolor")]).depth, ColorDepth::Ansi16);
        assert_eq!(env(&[("TERM", "xterm-256color")]).depth, ColorDepth::Ansi256);
        assert_eq!(env(&[("TERM", "xterm-ghostty"), ("COLORTERM", "truecolor")]).depth, ColorDepth::TrueColor);
        assert_eq!(env(&[("TERM", "linux")]).depth, ColorDepth::Ansi16);
        assert_eq!(env(&[("TERM", "dumb")]).depth, ColorDepth::Mono);
    }
    #[test]
    fn unicode_and_switches() {
        let e = env(&[("LANG", "en_US.UTF-8"), ("P95_NERD_FONT", "1"), ("P95_REDUCED_MOTION", "true")]);
        assert!(e.unicode && e.nerd_font && e.reduced_motion);
        assert!(!env(&[("LANG", "C")]).unicode);
        assert!(!env(&[("LANG", "en_US.UTF-8"), ("P95_ASCII", "1")]).unicode);
        assert!(!env(&[("LANG", "C"), ("P95_NERD_FONT", "1")]).nerd_font, "nerd font needs unicode");
        assert!(!env(&[("P95_REDUCED_MOTION", "0")]).reduced_motion);
    }
}
