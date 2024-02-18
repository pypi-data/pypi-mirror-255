# strava-ical

[![PyPI Python Version badge](https://img.shields.io/pypi/pyversions/strava-ical)](https://pypi.org/project/strava-ical/)
[![PyPI Version badge](https://img.shields.io/pypi/v/strava-ical)](https://pypi.org/project/strava-ical/)
![License badge](https://img.shields.io/github/license/liskin/strava-ical)

## Overview

**Generate iCalendar with your [Strava][] activities**

Uses [strava-offline][] to keep and incrementally sync with a local database of activities.

![Example screenshot of the output in Google Calendar](https://github.com/liskin/strava-ical/assets/300342/71d2e9c5-f9ef-481c-b5ee-4a71fd09caa4)

[strava-offline]: https://github.com/liskin/strava-offline#readme
[Strava]: https://strava.com/

## Installation

Using [pipx][]:

```
pipx ensurepath
pipx install "strava-ical[strava]"
```

To keep a local git clone around:

```
git clone https://github.com/liskin/strava-ical
make -C strava-ical pipx
```

Alternatively, if you don't need the isolated virtualenv that [pipx][]
provides, feel free to just:

```
pip install "strava-ical[strava]"
```

If you've already installed [strava-offline][] and use it separately, you can
omit the `[strava]` bit to avoid installing strava-offline twice.

[pipx]: https://github.com/pypa/pipx

## Setup and usage

* Run `strava-ical-sync` (or `strava-offline sqlite` if you chose to install
  [strava-offline][] separately) to synchronize activities metadata to a local
  sqlite database. This takes a while: first time a couple dozen seconds, then
  it syncs incrementally which only takes a few seconds each time. Add `-v` to
  see progress.

  The first time you do this, it will open Strava in a browser and ask for
  permissions. Should you run into any trouble at this point, consult
  [strava-offline][] readme or open an issue.

  If you make changes to older activities (to assign a different bike to a
  ride, for example), you may need a `--full` re-sync rathen than the default
  incremental one. See the [note about incremental synchronization](https://github.com/liskin/strava-offline#note-about-incremental-synchronization)
  for a detailed explanation.

* Run `strava-ical`:

  ```
  $ strava-ical --max-size 1M -o strava-activities.ical
  ```

* Import `strava-activities.ical` into your calendar app of choice.

  (Note that Google Calendar refreshes iCal URLs once a day and cannot be
  tweaked in any way. Manual refresh isn't possible either.)

## Command line options

<!-- include tests/readme/help.md -->
<!--
    $ export COLUMNS=120
-->

    $ strava-ical --help
    Usage: strava-ical [OPTIONS]
    
      Generate iCalendar with your Strava activities
    
    Options:
      --csv FILENAME          Load activities from CSV instead of the strava-offline database (columns: distance,
                              elapsed_time, id, moving_time, name, start_date, start_latlng, total_elevation_gain, type)
      --strava-database PATH  Location of the strava-offline database  [default:
                              /home/user/.local/share/strava_offline/strava.sqlite]
      -o, --output FILENAME   Output file  [default: -]
      -m, --max-size SIZE     Maximum size of the output file in bytes (accepts K and M suffixes as well)
      --help                  Show this message and exit.
<!-- end include -->

## Donations (♥ = €)

If you like this tool and wish to support its development and maintenance,
please consider [a small donation](https://www.paypal.me/lisknisi/5EUR) or
[recurrent support through GitHub Sponsors](https://github.com/sponsors/liskin).

By donating, you'll also support the development of my other projects. You
might like these:

* [strava-offline](https://github.com/liskin/strava-offline) – Keep a local mirror of Strava activities for further analysis/processing
* [strava-gear](https://github.com/liskin/strava-gear) – Rule based tracker of gear and component wear primarily for Strava
* [strava-map-switcher](https://github.com/liskin/strava-map-switcher) – Map switcher for Strava website
* [foursquare-swarm-ical](https://github.com/liskin/foursquare-swarm-ical) – Sync Foursquare Swarm check-ins to local sqlite DB and generate iCalendar
