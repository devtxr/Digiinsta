# Instagram Digital Store — Vercel + Python + MongoDB

A starter digital-product selling backend with an Instagram webhook and a Telegram inline-button admin panel.

## Features
- Python/FastAPI on Vercel
- MongoDB products and orders
- Instagram webhook + basic keyword replies
- Telegram admin panel with inline buttons
- Product activation/deactivation
- Order/revenue statistics
- Product/order data model ready for payment integration

## Deploy
1. Push this folder to GitHub.
2. Import the repository into Vercel.
3. Add all variables from `.env.example`.
4. Deploy.
5. Set Telegram webhook to `https://YOUR_DOMAIN/api/telegram/webhook`.
6. Configure the Instagram/Meta webhook callback as `https://YOUR_DOMAIN/api/instagram/webhook` and use the same verify token.

## Add product
In Telegram admin:
`/add Product Name | Description | 299 | https://example.com/file.zip | https://example.com/image.jpg`

> Payment verification is intentionally separated from the starter. Connect your chosen payment provider's server-to-server webhook before marking an order as paid and delivering the file.
