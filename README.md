# BT Speaker for Home Assistant

Connect any Bluetooth A2DP speaker to Home Assistant.

## Installation

### Add-on (required first)
1. Go to **Settings → Add-ons → Add-on Store**
2. Click ⋮ → **Repositories**
3. Add: `https://github.com/nzangel/BT_Speaker`
4. Install **BT Speaker** add-on and start it

### Integration (via HACS)
1. Open HACS → Integrations
2. Search **BT Speaker** → Install
3. Restart Home Assistant
4. Go to Settings → Integrations → Add BT Speaker

## Usage
Call service `bt_speaker.scan` to discover speakers,
then `bt_speaker.connect` with the MAC address.