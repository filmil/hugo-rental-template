## Approaches

- Prefer working on each new feature in a separate git worktree.
  - If possible, use `../` as the worktree base dir.

- All building to be done using `bazel`. If scripts are needed, make them
  so they can be invoked using `bazel run`.

- Make each new fix or feature request a separate pull request.

- Before working on a new feature request, ensure you start work from a fresh
  repository, which is synced with remote `main` branch.

## Invariants

- We have two separate sites: https://www.yourdomain.com, and
  https://book.yourdomain.com, they *must* look exactly alike.

  - When adding an item into the top navbar of one site, add an identical
    one in the other.

- When adding photos, always review them specially to ensure they are topical
  per this guide.

## Article advice

Apply when creating articles:

- Hyperlink main topics.
  - For each hyperlink, try to find and include a representative photo.
    - For seaside, use lively, bright, clear sky, bright sand photos.
    - Ensure photos are either ours or under liberal license.
      - Disclose the image source and licensing for each photo that is
        not ours.
 - Linking
   - Always include an invitation to visit and the appropriate booking link.

- When creating a new article, schedule it to be published a week after the
  newest article publication date (no matter if the said newest article is
  draft or not)

## Git management advice

- When fixing an issue, always note issue number in the PR and commits as:
  `Fixed: #NNN` where `NNN` is the number of the issue being fixed.
  This will auto-fix an issue once PR is merged.

- Check open issues in the repository. Ask user if they want you to pick one
  to work on.

## Desirable topics

- Desirable topics: similar to those a well-known vacation-rental brand would
  cover, but for our destinations.

  - The mountains (Mountain Town, State)
    - Ski resort events.
    - Venues.
    - Restaurants.
    - Nearby events and attractions.
    - Add photos, prefer skiing photos for winter, and hiking photos for
      summer.
    - Tips about the surrounding towns and the nearest national park.

  - The coast (Beach City, State)
    - Festivals.
    - Beach events.
    - Prefer photos showing sand, sea, clear sky and bright sun.

  - The far north (Northern City, Country)
    - Equipment rentals.
    - Aurora and wildlife tours.
    - Transportation.
    - Prefer photos showing wintertime.
    - Prefer photos showing nature to photos showing urban clutter.
    - Add notes about nearby ski slopes.

## Avoid topics

- Avoid topics (illustrative examples; adapt per destination):

  - The mountains:
    - Wildfire season.
    - Road closures in the wintertime.

  - The coast:
    - Hurricane season.

  - The far north:
    - Off-season caveats and anything that discourages a visit.
