# T.10: the monthly article generator


A checked-in, reviewable pipeline that front-loads a batch of destination
blog posts each month. Nothing publishes without a human: every generated
post is `draft: true`, and the batch arrives as a pull request.


## Pieces

* `topics.yaml` -- the topic queue, per destination, with season hints,
  image preferences and banned topics. Extend a list to add work; the
  generator takes the next unwritten topic.
* `prompt.md` -- the generation prompt handed to `claude -p`. House prose
  rules, the front-matter shape, the linkify and licensed-image
  requirements, and the `IMAGE:` placeholder convention.
* `pick_topics.py` -- selects the next N unwritten topics, round-robin
  across destinations. A topic is "written" once a post with its slug
  exists.
* `fetch_images.py` -- resolves each `IMAGE:<query>` placeholder to an
  appropriately licensed Wikimedia Commons photo, downloads and resizes it
  into `static/img/auto/`, and writes the attribution into the caption.
  Only CC0/CC BY/CC BY-SA/public-domain images are accepted; an
  unresolvable figure is dropped rather than shipped unlicensed.
* `../generate_articles.sh` -- the driver: branch, generate, resolve
  images, build, run the reference preflight, commit, open a PR.
* `rental-articles.{service,timer}` -- a systemd user unit pair to run it
  monthly.


## Run it by hand

    scripts/generate_articles.sh            # one post per destination + PR
    scripts/generate_articles.sh --count 1  # a single post
    scripts/generate_articles.sh --no-pr    # branch + commit only


## Arm the monthly timer

Edit the `WorkingDirectory` and `ExecStart` paths in
`rental-articles.service` to point at your checkout first, then:

    mkdir -p ~/.config/systemd/user
    cp scripts/t10/rental-articles.service ~/.config/systemd/user/
    cp scripts/t10/rental-articles.timer   ~/.config/systemd/user/
    systemctl --user daemon-reload
    systemctl --user enable --now rental-articles.timer
    systemctl --user list-timers rental-articles.timer

`loginctl enable-linger $USER` lets the timer fire while you are logged out.
Logs: `journalctl --user -u rental-articles`.


## Review flow

The generator opens a PR of `draft: true` posts. For each: read it, check
the facts and the image licence, adjust the prose, then remove the
`draft: true` line to publish. Future-dated posts also wait for their date.
