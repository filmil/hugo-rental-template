

# hugo-rentaltheme


The Hugo theme for [www.yourdomain.com][site]: meant to mirror your external booking site.
Poppins, black ink on `#F8F8F8`,
white surfaces, 10px buttons, 5px tag pills, and the black footer, all
matched to the look of your booking site at [book.yourdomain.com][book].

[site]: https://www.yourdomain.com
[book]: https://book.yourdomain.com

The theme is light-only by design. The booking site has no dark mode, and
the two properties are meant to be indistinguishable in feel.

Consumed by vendoring into `yourdomain.com.template//third_party/rentaltheme`
with git-vendor; the `BUILD.bazel` here carries the `hugo_theme` target the
site's Bazel build uses, so `git-vendor update` keeps the two in sync.


## Site parameters

| Param | Meaning |
| --- | --- |
| `description` | meta description |
| `favicon` | favicon path, default `/favicon.png` |
| `logo` | header logo path (fixed-dark ink: the bar is white in every scheme) |
| `footerLogo` | footer logo path (fixed-light ink: the footer is black), default `logo` |
| `brandTextA` | first, muted part of the typeset wordmark (e.g. "Your") |
| `brandTextB` | second, full-ink part of the wordmark (e.g. "Cat") |
| `gtag` | GA4 measurement id; omit for no analytics |
| `footer` | markdown footer line; `{Year}` is substituted |
| `copyright` | copyright holder, default site title |
| `cookieLink` | href for the "Cookie Preferences" footer link |

Page front matter: `title`, `date`, `tags`, `slug`, `draft`.
