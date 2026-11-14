# OpenInvento for Home Assistant

[![GitHub Release](https://img.shields.io/github/v/release/openinvento/homeassistant-openinvento?sort=semver)](https://github.com/openinvento/homeassistant-openinvento/releases)
[![Marketplace](https://img.shields.io/badge/Home%20Assistant-Marketplace-blue.svg)](https://next.home-assistant.io/integrations/marketplace/)
[![License](https://img.shields.io/github/license/openinvento/homeassistant-openinvento)](LICENSE)

Connect [OpenInvento](https://github.com/openinvento/openinvento) inventory
instances to Home Assistant using the OpenInvento REST API.

## Features

- Inventory, entry, article, and area counts
- Low-stock article sensor
- Inventory and entry details in sensor attributes
- Actions for creating, updating, and deleting inventory entries
- Support for self-signed or otherwise unverified TLS certificates
- Configured entirely from the Home Assistant UI

## Installation

### Home Assistant Marketplace

Home Assistant 2026.11 and newer includes HACS as the **Marketplace**. No
separate HACS installation is required.

1. Open **Settings → Marketplace** in Home Assistant.
2. Search for **OpenInvento**.
3. Open the integration and select **Download**.
4. Restart Home Assistant if prompted.

If this repository is not yet in the Marketplace catalog, add it as a custom
repository from the Marketplace settings.

On Home Assistant 2026.11 and older, use the
[HACS](https://hacs.xyz/docs/use/) integration instead.

### Manual

Copy the `custom_components/openinvento` directory into the
`custom_components` directory of your Home Assistant configuration, then
restart Home Assistant.

## Configuration

1. Open **Settings → Devices & services**.
2. Select **Add integration**.
3. Search for **OpenInvento**.
4. Enter the instance URL and an OpenInvento API key.
5. Keep **Verify SSL certificate** enabled unless the instance uses a
   self-signed or otherwise unverified certificate.

API keys can be created in OpenInvento under **Settings → API Keys**.

## Sensors

The integration creates one OpenInvento device with these sensors:

| Sensor | State | `items` attribute |
| --- | ---: | --- |
| `sensor.openinvento_articles` (Articles) | Article count | Article entries |
| `sensor.openinvento_areas` (Areas) | Area count | Area entries |
| `sensor.openinvento_low_stock` (Low stock items) | Tracked articles with quantity `≤ 0` | Low-stock entries |
| `sensor.openinvento_entries` (Inventory entries) | Total entry count | All entries |
| `sensor.openinvento_inventories` (Inventories) | Inventory count | Inventory UUIDs and names |

Example template:

```jinja
{{ state_attr('sensor.openinvento_low_stock', 'items') }}
```

## Actions

### `openinvento.create_entry`

Creates an area, shelf, box, or article.

```yaml
action: openinvento.create_entry
data:
  inventory: 4f9d2a3e-7a1b-4b2e-8c3d-1e2f3a4b5c6d
  type: article
  name: Raspberry Pi 5
  quantity: 3
  stock_tracking: true
```

### `openinvento.update_entry`

Updates an existing entry. Only fields that should change need to be supplied.

```yaml
action: openinvento.update_entry
data:
  uuid: e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b
  quantity: 2
```

### `openinvento.delete_entry`

Deletes an entry.

```yaml
action: openinvento.delete_entry
data:
  uuid: e1f2a3b4-c5d6-7e8f-9a0b-1c2d3e4f5a6b
```

## Support

- [OpenInvento documentation](https://openinvento.github.io/docs/)
- [External API documentation](https://openinvento.github.io/docs/docs/openinvento/externalAPI)
- [Report an issue](https://github.com/openinvento/homeassistant-openinvento/issues)
