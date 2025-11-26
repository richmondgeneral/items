# Square Catalog API Reference

## Location & Merchant IDs

- **Location ID:** B87BAEZ0NWV34 (Richmond General - ACTIVE)
- **Merchant ID:** 7MM9AFJAD0XHW

## Categories

Query categories with: `catalog.listCatalog` with `types: ["CATEGORY"]`

Common categories for vintage items:
- Books & Media
- Home & Garden
- Collectibles
- Art & Decor

## Creating Catalog Items

### Endpoint
`catalog.upsertCatalogObject`

### Minimal Item Creation

```json
{
  "idempotency_key": "uuid-v4-here",
  "object": {
    "type": "ITEM",
    "id": "#temp-id",
    "item_data": {
      "name": "Product Name",
      "description": "Description with <br> for line breaks",
      "variations": [{
        "type": "ITEM_VARIATION",
        "id": "#temp-var-id",
        "item_variation_data": {
          "item_id": "#temp-id",
          "name": "Regular",
          "sku": "RG-0001",
          "pricing_type": "FIXED_PRICING",
          "price_money": {
            "amount": 1999,
            "currency": "USD"
          }
        }
      }]
    }
  }
}
```

### With Images

Images must be uploaded separately via `catalog.createCatalogImage`:

```json
{
  "idempotency_key": "uuid-v4-here",
  "image": {
    "type": "IMAGE",
    "id": "#temp-image-id",
    "image_data": {
      "name": "Product Image",
      "caption": "Front view"
    }
  },
  "object_id": "EXISTING_ITEM_ID"
}
```

## Payment Links

### Endpoint
`checkout.createPaymentLink`

### Quick Pay (Simple)

```json
{
  "idempotency_key": "uuid-v4-here",
  "quick_pay": {
    "name": "Item Name",
    "price_money": {
      "amount": 1999,
      "currency": "USD"
    },
    "location_id": "B87BAEZ0NWV34"
  },
  "checkout_options": {
    "ask_for_shipping_address": true
  }
}
```

### Response

```json
{
  "payment_link": {
    "id": "LINK_ID",
    "url": "https://square.link/u/XXXXXXXX",
    "long_url": "https://checkout.square.site/merchant/..."
  },
  "related_resources": {
    "orders": [{ "id": "ORDER_ID" }]
  }
}
```

## Useful Queries

### List All Items
```
catalog.listCatalog with types: ["ITEM"]
```

### Search by SKU
```
catalog.searchCatalogItems with text_filter containing SKU
```

### Get Item Details
```
catalog.retrieveCatalogObject with object_id
```

## Price Formatting

- Prices in **cents** (integer)
- $19.99 = `1999`
- $5.00 = `500`
- Always USD for Richmond General
