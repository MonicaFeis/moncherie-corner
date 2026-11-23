# Moncherie corner 車厘小角

![Moncherie corner home page](docs/screenshots/feature-home.png)

**Moncherie corner** is a small online shop for my own hand-drawn art, in the style of a 1960s Hong Kong cha chaan teng (茶餐廳). Customers can buy digital sticker sets, postcards, website art, and order a custom portrait drawn by hand.

- **Live site:** [moncherie-corner-d07b8510a19e.herokuapp.com](https://moncherie-corner-d07b8510a19e.herokuapp.com/)
- **GitHub:** [github.com/MonicaFeis/moncherie-corner](https://github.com/MonicaFeis/moncherie-corner)

> Payments use Stripe in **test mode**. No real money is taken.
> Test card: `4242 4242 4242 4242`, any future date, any CVC, any postcode.

---

## Contents

1. [Purpose and value](#purpose-and-value)
2. [User experience (UX)](#user-experience-ux)
3. [Features](#features)
4. [Data model](#data-model)
5. [Project structure](#project-structure)
6. [Security and permissions](#security-and-permissions)
7. [Testing](#testing)
8. [Bugs fixed](#bugs-fixed)
9. [Deployment](#deployment)
10. [Technologies](#technologies)
11. [Credits](#credits)

---

## Purpose and value

I am an illustrator and designer from Hong Kong, based in Germany. I draw stickers, postcards and portraits under the name **Moncherie**. Before this project, I had no place where people could buy my work directly. I am also finishing my training as full stack web developer. So this shop is also my final project.

Moncherie corner is that place. It is a real shop with real products:

| Product | What the customer gets |
|---|---|
| **Sticker sets** | A ZIP file with transparent PNG stickers, to download right after payment |
| **Postcards** | A print ready file to download, **or** a real A6 postcard posted to them |
| **Website art** | Tile patterns and retro frames for their own website, to download |
| **Custom portraits** | A portrait drawn by hand from their photos, as a file or a printed 17 cm x 17 cm posted to them |

**Who it is for**

- People from Hong Kong (in Hong Kong or abroad) who like the old cha chaan teng feeling
- People in Germany or people around the world, who like hand drawn, cosy designs (Christmas, German bakery)
- Small website owners who want original background patterns
- Families and pet owners who want a personal portrait as a gift

**Why customers register:** an account keeps their orders and downloads in one place. They can download their files again for 30 days, follow a printed order, send photos for a portrait, and write reviews for things they bought.

The whole shop is **bilingual**: Cantonese (繁體中文) and English, because many of my customers can read both, and because it shows my brand and my identity (a Hong Konger who moved to Germany).
---

## User experience (UX)

### User stories

**Roles:** Visitor (not logged in), Customer (registered), Owner (staff user).
**Priority (MoSCoW):** Must = needed to pass. Should = build if time allows. Could = only if spare time. Won't = decided not to build in this release.

Each story has acceptance criteria (Given … when … then …). Click a section to open it.

<details>
<summary><strong>1. Accounts</strong> (US-01 to US-03)</summary>

**US-01 Register (Must)**
As a visitor, I want to create an account so that I can buy products and keep my downloads.
- Given I enter a unique username, a valid email and a strong password, when I submit, then my account is created and I am logged in.
- Given the username or email is already taken, when I submit, then I see a clear error and nothing is created.

**US-02 Log in and out (Must)**
As a customer, I want to log in and out so that my orders stay private.
- Given correct details, when I log in, then I see a success message and my name in the navbar.
- Given I log out, then my session ends and My downloads is no longer reachable.

**US-03 Anonymous only pages (Must)**
As a logged in user, I should not see the login or register pages.
- Given I am logged in, when I open /accounts/login/ or /accounts/register/, then I am redirected to the home page.

</details>

<details>
<summary><strong>2. Browsing</strong> (US-04 to US-06)</summary>

**US-04 Browse by category (Must)**
As a visitor, I want to filter products by category so that I find what I need quickly.
- Given I choose a category, then only active products in it are listed.
- Given a product is hidden, then it never appears in lists or search.

**US-05 Product page (Must)**
As a visitor, I want to see a product's images, description, price and type so that I can decide to buy.
- Given I open a product, then I see its image, description, price, category and an Add to cart button.

**US-06 Search and sort (Could)**
As a visitor, I want to search by name and sort by price.

</details>

<details>
<summary><strong>3. Bag</strong> (US-07 to US-09)</summary>

**US-07 Add to cart (Must)**
As a visitor or customer, I want to add a product to my cart.
- Given I click Add to cart, then the cart count updates and I see a confirmation message.
- Given the product is already in my cart and is a digital product, then it is not added twice.

**US-08 Remove from cart (Must)**
As a visitor or customer, I want to remove an item so that I only pay for what I want.
- Given I remove an item, then the list and the total update immediately.

**US-09 Trustworthy total (Must)**
As a customer, I want the cart total to be correct.
- Given any cart, then the total is calculated on the server from database prices, never from values sent by the browser.

</details>

<details>
<summary><strong>4. Checkout and payments</strong> (US-10 to US-13)</summary>

**US-10 Pay with Stripe (Must)**
As a customer, I want to pay securely so that I can get my files.
- Given I am logged in with items in my cart, when I click Checkout, then a pending order is created and I am sent to Stripe Checkout.
- Given I am not logged in, when I click Checkout, then I am asked to log in and my cart is kept.

**US-11 Successful payment (Must)**
As a customer, I want clear confirmation after paying.
- Given Stripe confirms payment, then the order is marked paid (by the webhook only), my cart is cleared and I see the thank you page.

**US-12 Failed or cancelled payment (Must)**
As a customer, I want to know when a payment did not go through.
- Given I cancel or the card fails, then I see the payment failed page, nothing is marked paid and my cart is kept.

**US-13 Webhook safety (Must)**
As the owner, I want only real Stripe events to mark orders paid.
- Given a request with an invalid signature, then it is rejected.
- Given the same event arrives twice, then the order is only updated once.

</details>

<details>
<summary><strong>5. Orders and downloads</strong> (US-14 to US-15)</summary>

**US-14 My orders (Must)**
As a customer, I want to see my past orders.
- Given I have orders, then I see only my own, newest first. Given I have none, then I see the empty state.

**US-15 My downloads (Must)**
As a customer, I want to download what I bought.
- Given a paid order, when I click Download, then I receive the file.
- Given an unpaid order or another customer's file, then I get a 403 or 404.

</details>

<details>
<summary><strong>6. Reviews</strong> (US-16 to US-17)</summary>

**US-16 Review a product I bought (Should)**
As a customer, I want to rate and comment on a product I bought.
- Given I bought it, then I can create a review with a rating from 1 to 5 and a comment.
- Given I did not buy it, then I cannot review it.

**US-17 Edit or delete my review (Should)**
- Given my own review, then I can edit or delete it. Given someone else's, then I cannot.

</details>

<details>
<summary><strong>7. Owner: product management</strong> (US-18 to US-21)</summary>

**US-18 Add a product (Must)**
As the owner, I want to add a product with an image and description so that customers can buy it.
- Given I fill in name, category, price above 0, description, preview image and download file, when I save, then the product appears in the shop.
- Given the price is 0 or negative or the image is the wrong type or too big, then I see a validation error.

**US-19 Edit a product (Must)**
- Given an existing product, when I change any field and save, then the shop shows the new details immediately.

**US-20 Delete a product (Must)**
- Given I click Delete, then I must confirm first.
- Given the product was never bought, then it is deleted.
- Given customers already bought it, then it is hidden instead, so their downloads keep working.

**US-21 Owner only access (Must)**
- Given I am not staff, when I open any /manage/ page, then I get a 403 and no data.

</details>

<details>
<summary><strong>8. Custom portraits</strong> (US-22 to US-25, US-44, US-45)</summary>

**US-22 Choose a portrait version (Should)**
As a customer, I want to choose a digital file or a printed 17cm x 17cm and how many people or pets are in the portrait, so that I see the right price.
- Given I choose a version or change the number of people or pets, then the price on the page updates straight away (JavaScript preview).
- Given I add it to my bag, then the server works out the price again from the database (base price + version + €10 for each extra person or pet).
- Given I choose the printed version, then checkout asks for shipping. Given I choose the digital file, then it does not.

**US-23 Send names and photos (Should)**
As a customer, I want to tell the artist the names and my ideas and upload photos, so that the portrait looks like us.
- Given my bag has a portrait, then checkout shows a names and notes box and a photo upload (1 to 5 photos, pictures only, up to 10 MB each).
- Given I upload a file that is not a picture, or too many photos, then I see a clear error and no order is made.
- Given my payment fails or is cancelled, then my photos are deleted, because they are private.

**US-24 Deliver the portrait (Should)**
As the owner, I want to see portrait orders and upload the finished drawing.
- Given I open Manage → Orders → Portraits to draw, then I see every paid portrait that is not delivered yet.
- Given I open one, then I see the names, notes and reference photos, and an upload box.
- Given I upload the finished file, then the customer can download it from My downloads, and only that customer can.

**US-25 Accept or request changes (Could)**
- Given a delivered portrait, then the customer can accept it or request one round of changes.

**US-44 Know my portrait is being drawn (Should)**
As a customer, I want to know my portrait is not an instant download.
- Given I look at the portrait page, the Stripe page, the thank-you page or the confirmation email, then it says the portrait is hand-drawn and usually ready within 7 days.
- Given I paid but the portrait is not delivered yet, then My downloads shows a "畫緊 Being drawn" picture and my order number instead of a download button.

**US-45 See only this order after paying (Should)**
As a customer, I want the thank-you page to show only what I just bought.
- Given I click My downloads on the thank-you page, then I see only this order, with a link to see all my downloads.

</details>

<details>
<summary><strong>9. General</strong> (US-26 to US-29)</summary>

**US-26 Friendly errors (Must)**
- Given a page that does not exist, then I see the 404 page with a link back to the shop.

**US-27 Navigation and layout (Must)**
- Given any page, then I see the main menu, a cart count and my login state.

**US-28 Accessible and responsive (Must)**
- Given a phone, tablet or desktop, then the layout works, images have alt text and text has enough contrast.

**US-29 Secure deployment (Must)**
- Given the deployed site, then DEBUG is off, no secrets are in git and Stripe runs in test mode.

</details>

<details>
<summary><strong>10. Additions: confirmation, failures, Stripe messages, delivery</strong> (US-30 to US-38)</summary>

**US-30 Order confirmation email (Should)**
As a customer, I want an email after paying so that I have proof and a link to my files.
- Given the webhook marks my order paid, then I receive one email with the order number, items, total and a link to My downloads.
- Given the same webhook event arrives twice, then only one email is sent.

**US-31 Order detail page (Must)**
As a customer, I want to see the details of one order.
- Given I open one of my orders, then I see its status, items, total and date. Given it is another customer's order, then I get a 403 or 404.

**US-32 Abandoned or expired checkout (Should)**
As a customer, I want a failed or abandoned payment to be handled clearly.
- Given I cancel, then I see the payment failed page and the order is marked cancelled.
- Given I leave Stripe and the session expires, then the order is marked expired and no download is unlocked.

**US-33 Stripe checkout messaging (Should)**
As a customer, I want a friendly message on the Stripe page.
- Given I reach Stripe Checkout, then I see the shop's logo and colours and a short thank you message.

**US-34 Delivery information (Must)**
As a customer, I want to know how I will receive my purchase.
- Given a digital product, then the product page and checkout say it is an instant download. Given a commission, then they give the expected delivery time.

**US-35 Choose a shipping method (Should)**
As a customer, I want to choose how my printed items are shipped so that they reach me.
- Given my cart has a physical item, then I must enter a shipping address and choose a method before paying, and I see the shipping cost.
- Given my cart has only digital items, then I see no shipping step.
- Given I choose a method, then the server adds its cost from the database to the total.

**US-36 Owner ships orders (Should)**
As the owner, I want to see paid physical orders and mark them shipped so that customers know where their order is.
- Given a paid order with physical items, then it appears in my orders list with the address and chosen method.
- Given I mark it shipped and add a tracking number, then the customer sees the status and number on the order detail page.

**US-37 Manage shipping methods (Could)**
As the owner, I want to add or edit shipping methods (name, price, delivery days) without changing code.

**US-38 Stock (Could)**
As a customer, I should not be able to add an out-of-stock printed product to my cart.

</details>

<details>
<summary><strong>11. Email notifications (the notifications app)</strong> (US-39 to US-43)</summary>

Each email is one small function (for example `send_order_confirmation(order)`) with a text and an HTML template. While developing, emails print in the terminal. On the live site they go out through an email service set up with environment variables.

**US-39 Welcome email (Should)**
As a new customer, I want a short welcome email so that I know my account works.
- Given I register, then I receive one welcome email.

**US-40 Payment unsuccessful email (Should)**
As a customer, I want to be told when my payment did not go through.
- Given my payment fails or my checkout expires, then I receive an email that says nothing was charged and links back to my cart.

**US-41 Shipped email (Should)**
As a customer, I want to know when my printed order has shipped.
- Given the owner marks my order as shipped, then I receive an email with the tracking number.

**US-42 Portrait delivered email (Should)**
As a customer, I want to know when my portrait is ready.
- Given the owner uploads my finished portrait, then I receive one email in the shop style (logo, 車厘小角, bilingual text) with a link to My downloads.
- Given I chose the printed version, then the email also says the print will be posted to me.

**US-43 Password reset email (Could)**
As a customer, I want to reset a forgotten password by email.
- Given I enter my email on the reset page, then I receive a reset link.

US-30 (order confirmation email) also belongs to this app. Email functions are called from the Stripe webhook and the owner pages, and they do not need new database tables.

</details>

<details>
<summary><strong>12. Friendly pages and scope decisions</strong> (US-46 to US-50)</summary>

**US-46 Friendly shop sign pages (Should)**
As a visitor, I want error and empty pages to look like part of the shop so that I feel looked after, not lost.
- Given a page that does not exist, then I see the 搵唔到 *Page not found* sign and a link back to the shop (404).
- Given I open an owner only page without permission, then I see the 唔好意思 sign (403).
- Given the server has a problem, then I see the 好忙呀 sign and a short message to try again later (500).
- Given my bag is empty, then I see the 空空如也 *Nothing here yet* sign and a link to the shop.
- Given I log out, then I see the 收工啦 sign.
- Given my payment worked, then the success page shows the 開心啲 sign.
- Given a category has no products, then I see the 繼續努力 sign and a link to all products.
- Every sign has alt text that describes the picture and its words.

#### Won't have (this release)

These were planned but left out on purpose. They would be the next steps after the course.

**US-47 Save favourites (Won't)**
As a customer, I want to save products to a favourites list so that I can find them again later.

**US-48 Back in stock email (Won't)**
As a customer, I want to be emailed when a sold-out printed item is back in stock.

**US-49 Seasonal discount codes (Won't)**
As a customer, I want to use a seasonal discount code at checkout.
- Left out because it changes the prices sent to Stripe, the order totals and the emails, which is too risky to add close to the deadline.

**US-50 Tote bag (Won't)**
As a customer, I want to buy a printed tote bag.
- The product is hidden (not active) instead of deleted, so older test orders still work.

</details>


The project was built in small steps, so there was always a shop that worked from start to finish:

1. **MVP (all Must stories):** accounts, browsing, bag, Stripe checkout, downloads, owner product pages, deployment
2. **Should, step 1:** printed products with stock and shipping, owner order pages, Stripe success and failure messages
3. **Should, step 2:** custom portraits (versions, people and pets, photo upload and delivery)
4. **Should, step 3:** emails, reviews, the featured carousel and the friendly shop sign pages
5. **Won't (this release):** favourites, back-in-stock emails, discount codes and a tote bag were planned but left out on purpose, so the finished features could be tested properly before the deadline.

### Design

The design is based on my own poster *德國製造 Made in Germany*: I am in a Hong Kong cha chaan teng, drawn in a 1960s poster style.

**Colours**

| Name | Colour | Used for |
|---|---|---|
| Teal | `#14504F` | Navbar, footer, headings, buttons |
| Cream | `#F2E0C1` | Page background |
| Red | `#B02F22` | Main buttons, prices, important notes |
| Jade | `#17614A` | Tile strip, details |
| Gold | `#E0A84A` | Small highlights |

**Fonts** (Google Fonts)

- **Noto Serif TC** for headings, so Chinese (Cantonese) and English look good together
- **Noto Sans TC** for normal text
- **Playball** for the word *corner* in the logo, inspired by Hong Kong style neon signs.

**Hand drawn signs.** Instead of plain error pages, the shop uses shop signs that I drew, like the signs on an old cha chaan teng wall. For example: 搵唔到 *Page not found* (404), 好忙呀 *So busy* (500), 開心啲 *Be happy* (thank you), 空空如也 *Nothing here yet* (empty bag), 收工啦 *Home time* (logged out).

### Wireframes

Before building, I made low-fidelity wireframes for 16 screens, each for **desktop (1280 px), tablet (768 px) and phone (375 px)**.

| | |
|---|---|
| **01 Home**<br>[![Home wireframe](docs/wireframes/wireframe-01-home.png)](docs/wireframes/wireframe-01-home.png) | **02 Shop**<br>[![Shop wireframe](docs/wireframes/wireframe-02-shop.png)](docs/wireframes/wireframe-02-shop.png) |
| **03 Product (custom portrait)**<br>[![Product (custom portrait) wireframe](docs/wireframes/wireframe-03-product.png)](docs/wireframes/wireframe-03-product.png) | **04 Bag**<br>[![Bag wireframe](docs/wireframes/wireframe-04-bag.png)](docs/wireframes/wireframe-04-bag.png) |
| **05 Checkout**<br>[![Checkout wireframe](docs/wireframes/wireframe-05-checkout.png)](docs/wireframes/wireframe-05-checkout.png) | **06 Thank you**<br>[![Thank you wireframe](docs/wireframes/wireframe-06-thank-you.png)](docs/wireframes/wireframe-06-thank-you.png) |
| **07 Payment failed**<br>[![Payment failed wireframe](docs/wireframes/wireframe-07-payment-failed.png)](docs/wireframes/wireframe-07-payment-failed.png) | **08 Log in and register**<br>[![Log in and register wireframe](docs/wireframes/wireframe-08-login-register.png)](docs/wireframes/wireframe-08-login-register.png) |
| **09 My orders**<br>[![My orders wireframe](docs/wireframes/wireframe-09-my-orders.png)](docs/wireframes/wireframe-09-my-orders.png) | **10 Order detail**<br>[![Order detail wireframe](docs/wireframes/wireframe-10-order-detail.png)](docs/wireframes/wireframe-10-order-detail.png) |
| **11 My downloads**<br>[![My downloads wireframe](docs/wireframes/wireframe-11-my-downloads.png)](docs/wireframes/wireframe-11-my-downloads.png) | **12 Owner: manage products**<br>[![Owner: manage products wireframe](docs/wireframes/wireframe-12-owner-products.png)](docs/wireframes/wireframe-12-owner-products.png) |
| **13 Owner: add or edit product**<br>[![Owner: add or edit product wireframe](docs/wireframes/wireframe-13-owner-product-form.png)](docs/wireframes/wireframe-13-owner-product-form.png) | **14 Owner: orders**<br>[![Owner: orders wireframe](docs/wireframes/wireframe-14-owner-orders.png)](docs/wireframes/wireframe-14-owner-orders.png) |
| **15 Owner: one order**<br>[![Owner: one order wireframe](docs/wireframes/wireframe-15-owner-order.png)](docs/wireframes/wireframe-15-owner-order.png) | **16 Page not found (404)**<br>[![Page not found (404) wireframe](docs/wireframes/wireframe-16-404.png)](docs/wireframes/wireframe-16-404.png) |

Click a wireframe to see it full size.

**What changed after the wireframes**

- The categories changed from *Digital stickers, Prints and gifts, Portraits* to **Portraits, Postcards, Sticker sets and Website art**, to match the products I really made.
- The **tote bag** and **art prints** were left out (see at Won't in the user stories).
- The **Commission a portrait** button on the home page was removed, because the portrait is one of my products, like the others.
- The bag address changed from `/cart/` to **`/bag/`**, so it matches the word customers see to avoid any confusion.
- The empty and error states got my own hand drawn **shop signs** instead of plain illustrations.
- The portrait price became €20 for one person and €10 for each extra person or pet to make it more realistic.

### Accessibility

- Every picture has a useful `alt` text (or an empty one if it is only decoration)
- Headings go in order (h1, h2, h3), checked with W3C and WAVE
- Colours were checked for contrast: **0 contrast errors** in WAVE
- A **skip link** lets keyboard users jump straight to the main content
- Messages use `role="alert"`, and the Pay button tells screen readers when it is busy (`role="status"`)
- Chinese text is marked with `lang="zh-Hant-HK"`
- All pages work on phones, tablets and desktops (Bootstrap grid)

---

## Features

### Home page

The hero shows my poster with **歡迎光臨 Come on in**. Below it: the four categories with their own covers, a **featured carousel** (I choose which products are featured) and the newest happy reviews.

### Shop and product pages

![Product page](docs/screenshots/feature-product-detail.png)

- Products can be filtered by category
- Each product page has a large picture, examples (for portraits) and the reviews
- **Versions:** a postcard can be a digital file or a printed card. The price changes straight away when the customer chooses a version (JavaScript), and the server always works out the real price again.

![Choosing a version](docs/screenshots/feature-product-options.png)

- **Headings in descriptions:** the owner can start a line with `## ` in the description, and it becomes a highlighted heading on the page (for example *## 價錢 Price*). The text is escaped, so no HTML can be added.

### Stock

Digital products are always available, so stock `0` is fine for them. Stock is only counted for **printed postcards** and **portrait slots**. When a printed item is sold out, the shop shows *售罄 Sold out* and it cannot be added to the bag.

### Bag

![Bag](docs/screenshots/feature-bag.png)

- Add, update and remove items, with a green message and a 🛍️ icon each time
- A digital file can only be added once (you do not need two copies)
- The total updates straight away when the quantity changes (JavaScript preview)
- An empty bag shows the 空空如也 *Nothing here yet* sign

![Empty bag](docs/screenshots/feature-empty-bag.png)

In the code, the shopping bag app is called `cart` (a common name in Django shops). On the website, customers always see **bag** (購物袋), also in the web address `/bag/`.

### Checkout and payment

![Checkout](docs/screenshots/feature-checkout.png)

- **Edit my bag** button so customer can change their bag before paying.
- **Shipping** is only asked for when the bag has printed items

![Choosing shipping](docs/screenshots/feature-shipping.png)

- Payment with **Stripe Checkout**. Prices are worked out again on the server from the database, so nobody can change a price in the browser.
- The Pay button shows *去緊付款… Taking you to payment…* and cannot be clicked twice
- A **Stripe webhook** marks the order as paid, even if the customer closes the page
- The Stripe page uses the shop's colour, so customers can see it belongs to the shop and feel safe and secure.
- Stripe runs in test mode (sandbox), because full business account needs a registered business. That is why the Stripe page shows the sandbox name, not Moncherie corner.

![Stripe payment](docs/screenshots/feature-stripe.png)

### After paying

- **Success:** a thank-you page with the 開心啲 *Be happy* sign and a confirmation email

![Thank you page](docs/screenshots/feature-thank-you.png)

- **Failed or cancelled:** a friendly page, the bag is kept, and the customer can try again
- **My orders:** every order with its status and details
- **My downloads:** files can be downloaded for **30 days**, with a countdown. Only the customer who paid can download them.

![My downloads](docs/screenshots/feature-my-downloads.png)

### Custom portraits

1. The customer chooses a version (digital or printed 17 × 17 cm) and how many people or pets. The price is €20 for one, and €10 more for each extra person or pet.
2. At checkout, user can write their names and notes and upload up to 5 photos.
3. The thank-you page and My downloads show the **Being drawn** poster with a red note that it is usually ready within 7 days after payment.

![Portrait being drawn](docs/screenshots/feature-portrait-being-drawn.png)

4. I will upload the finished portrait. The customer gets an email and can download it for 30 days.

### Reviews

Customers can review a product **only after buying it**, from My downloads or their order page. They can edit or delete their own review. Each customer can review a product once.

### Emails

The shop sends emails from its own Gmail address (moncherie.corner@gmail.com) for: welcome, order confirmed, payment unsuccessful, order shipped and portrait ready.

![Order email](docs/screenshots/feature-email-digital.png)

### Owner pages

The owner (me or a staff user) can:

- **Add, edit and delete products** on the site (Manage), with validation, not only in the Django admin
- See all orders, mark printed orders as **shipped** (with a tracking number) and **deliver portraits**

![Admin](docs/screenshots/feature-admin-products.png)

---

## Data model

The database is **PostgreSQL** on Heroku (SQLite on my computer). The bag is stored in the **session**, so it is not a table.

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    USER ||--o{ REVIEW : writes
    CATEGORY ||--o{ PRODUCT : contains
    PRODUCT ||--o{ PRODUCT_OPTION : "has versions"
    PRODUCT ||--o{ PRODUCT_IMAGE : "has examples"
    PRODUCT ||--o{ REVIEW : receives
    PRODUCT ||--o{ ORDER_ITEM : "sold as"
    SHIPPING_METHOD ||--o{ ORDER : "used by"
    ORDER ||--|{ ORDER_ITEM : contains
    ORDER ||--o{ REFERENCE_PHOTO : "has (portraits)"

    USER {
        int id PK
        string username
        string email
        bool is_staff
    }
    CATEGORY {
        int id PK
        string name
        string slug
        text description
        image image
    }
    PRODUCT {
        int id PK
        int category_id FK
        string name
        string slug
        text description
        decimal price
        string product_type
        image image
        file download_file
        int stock
        int max_people
        decimal extra_person_price
        bool is_featured
        bool is_active
        datetime created_at
    }
    PRODUCT_OPTION {
        int id PK
        int product_id FK
        string name
        decimal extra_price
        bool is_printed
        int position
    }
    PRODUCT_IMAGE {
        int id PK
        int product_id FK
        image image
        string caption
        int position
    }
    REVIEW {
        int id PK
        int product_id FK
        int user_id FK
        int rating
        text comment
        datetime created_at
        datetime updated_at
    }
    SHIPPING_METHOD {
        int id PK
        string name
        decimal price
        int delivery_days
        bool is_active
    }
    ORDER {
        int id PK
        int user_id FK
        int shipping_method_id FK
        string status
        decimal shipping_cost
        text shipping_address
        text notes
        decimal total
        string stripe_session_id
        string tracking_number
        datetime created_at
    }
    ORDER_ITEM {
        int id PK
        int order_id FK
        int product_id FK
        string product_name
        string product_type
        decimal price
        int quantity
        string option_name
        int people
        bool is_printed
        file delivered_file
        datetime delivered_at
    }
    REFERENCE_PHOTO {
        int id PK
        int order_id FK
        image image
        datetime uploaded_at
    }
```

### What each model does

| Model | App | What it stores | Important rules |
|---|---|---|---|
| **User** | Django | The customer or the owner | `is_staff` = the owner (me)|
| **Category** | products | A group, for example Postcards | Unique name and slug. If there is no cover, the newest product picture is used |
| **Product** | products | Something for sale | `product_type` is `digital`, `printed` or `portrait`. `is_active` hides it from the shop without deleting it. The slug is made from the name |
| **ProductOption** | products | A version, for example *Printed A6 postcard* | `extra_price` is added to the price. `is_printed` means it is posted, so it does **not** unlock the download |
| **ProductImage** | products | Example pictures for a portrait | Shown on the product page |
| **Review** | reviews | Stars (1 to 5) and a comment | Only for products the customer bought. One review per product per customer |
| **ShippingMethod** | checkout | For example *Standard post* | Only used for printed items |
| **Order** | checkout | One purchase | Status: pending, paid, cancelled, expired or shipped |
| **OrderItem** | checkout | One line of an order | Keeps the name and price **at the time of buying**, so old orders stay correct if a product changes or is deleted. For portraits, it also holds the finished file |
| **ReferencePhoto** | checkout | A photo the customer sends for a portrait | Up to 5 per order |

**Custom models I wrote:** Category, Product, ProductOption, ProductImage, Review, ShippingMethod, Order, OrderItem and ReferencePhoto.

**CRUD**

| | Create | Read | Update | Delete |
|---|---|---|---|---|
| **Products** (owner) | Manage → Add | Shop, product page | Manage → Edit | Manage → Delete |
| **Reviews** (customer) | Leave a review | Product page | Edit | Delete |
| **Bag** (customer) | Add to bag | Bag page | Change quantity | Remove |
| **Orders** | Checkout | My orders | Owner marks shipped | Admin only |

---

## Project structure

The project has one Django app for each part of the shop, so each part could be reused.

| App | What it does |
|---|---|
| `config` | Settings, main URLs |
| `home` | Home page, the hero and carousel, the shop sign pages |
| `accounts` | Register, log in, log out |
| `products` | Categories, products, versions, owner product pages |
| `cart` | The bag, kept in the shopping session |
| `checkout` | Checkout, Stripe, webhook, orders, downloads, owner order pages |
| `reviews` | Reviews |
| `notifications` | All emails |

**URLs**

| Address | Page |
|---|---|
| `/` | Home |
| `/products/` and `/products/?category=postcards` | Shop and categories |
| `/products/<slug>/` | Product page |
| `/products/manage/` | Owner: products (only owner and her staff can manage products) |
| `/bag/` | Bag |
| `/checkout/` | Checkout |
| `/checkout/orders/` and `/checkout/downloads/` | My orders, My downloads |
| `/checkout/manage/` | Owner: orders |
| `/reviews/add/<slug>/` | Leave a review |
| `/accounts/register/`, `/accounts/login/` | Register, log in |

---

## Security and permissions

- **Secrets** (the Django secret key, Stripe keys, Cloudinary URL, Gmail app password) are only in a `.env` file on my computer and in the Heroku Config Vars. `.env` is in `.gitignore`, so it is never on GitHub.
- An early commit had a test `SECRET_KEY` in `settings.py`. I moved it to environment variables and made a new key for the live site, so the old one is no longer used.
- **DEBUG is off** on Heroku.
- On Heroku, all pages use **HTTPS**, and cookies are only sent over HTTPS.
- **Log in and Register** are only for visitors who are not logged in. Logged-in users are sent to the home page.
- **Owner pages** (Manage products, Manage orders) check `is_staff`. Other users get the 唔好意思 *403* sign page.
- **Downloads** check that the logged-in user really paid for the file, within 30 days.
- **Prices** are always worked out on the server. The **Stripe webhook** checks Stripe's signature before it marks an order as paid.
- Only the owner can use the Django admin.

---

## Testing

### Automated tests (TDD)

The project has **199 automated tests** (Django `TestCase`). I followed **test-driven development**: for most features, I first wrote the test and committed it (the test fails), then wrote the code that makes it pass. You can see this in the git history, with commits that start with *Test:*.

```
python3 manage.py test
```

![Django tests](docs/screenshots/django-tests.png)

The red text in the test output (for example *Not Found* or *Permission denied*) is expected: many tests check that wrong requests are blocked. The final **OK** means every test passed.

### Python: PEP8 (flake8)

All Python code is checked with **flake8**. The settings are in `.flake8` (lines up to 119 characters, migrations not checked).

```
python3 -m flake8
```

No output means no problems.

![flake8](docs/screenshots/flake8.png)

### HTML: W3C validator

Every page was checked with the [W3C Nu HTML Checker](https://validator.w3.org/nu/). Public pages were checked by address. Pages that need a login were checked by copying the page source (*text input*).

| Page | Result | Screenshot |
|---|---|---|
| Home | ✅ No errors or warnings | [view](docs/screenshots/w3c-home.png) |
| All products | ✅ | [view](docs/screenshots/w3c-products.png) |
| Category | ✅ | [view](docs/screenshots/w3c-category.png) |
| Product page | ✅ | [view](docs/screenshots/w3c-product-detail.png) |
| Portrait page | ✅ | [view](docs/screenshots/w3c-product-portrait.png) |
| 404 page | ✅ | [view](docs/screenshots/w3c-404.png) |
| Log in | ✅ | [view](docs/screenshots/w3c-login.png) |
| Register | ✅ | [view](docs/screenshots/w3c-register.png) |
| Logged out | ✅ | [view](docs/screenshots/w3c-logged-out.png) |
| Bag | ✅ | [view](docs/screenshots/w3c-cart.png) |
| Checkout | ✅ | [view](docs/screenshots/w3c-checkout.png) |
| Thank you | ✅ | [view](docs/screenshots/w3c-thank-you.png) |
| My orders | ✅ | [view](docs/screenshots/w3c-my-orders.png) |
| My downloads | ✅ | [view](docs/screenshots/w3c-my-downloads.png) |

The first check found a heading error on the shop pages ([before](docs/screenshots/w3c-before-heading-error.png)) and a warning on the reviews ([before](docs/screenshots/w3c-before-review-warning.png)). Both are fixed (see [Bugs fixed](#bugs-fixed)).

The email templates use inline styles, as email apps need. They are not part of the website validation.

### CSS: W3C Jigsaw

`static/css/style.css`: **No errors found.**

![Jigsaw](docs/screenshots/jigsaw-css.png)

### JavaScript: JSHint

All four JavaScript files were checked with [JSHint](https://jshint.com/), with `/* jshint esversion: 11 */`.

| File | What it does | Result | Screenshot |
|---|---|---|---|
| `carousel.js` | Featured carousel buttons | ✅ No warnings | [view](docs/screenshots/jshint-carousel.png) |
| `cart.js` | Bag total preview | ✅ No warnings (1 fixed) | [view](docs/screenshots/jshint-cart.png) |
| `checkout.js` | Pay button "please wait" | ✅ No warnings | [view](docs/screenshots/jshint-checkout.png) |
| `product.js` | Price preview, example pictures | ✅ No warnings | [view](docs/screenshots/jshint-product.png) |

### Lighthouse

Tested with Lighthouse (via [PageSpeed Insights](https://pagespeed.web.dev/)) on the live site.

| Page | Device | Performance | Accessibility | Best Practices | SEO | Screenshot |
|---|---|---|---|---|---|---|
| Home | Mobile | 86 | 100 | 100 | 100 | [view](docs/screenshots/lighthouse-home-mobile.png) · [before](docs/screenshots/lighthouse-home-mobile-before.png) |
| Home | Desktop | 91 | 100 | 100 | 100 | [view](docs/screenshots/lighthouse-home-desktop.png) |
| All products | Mobile | 74 | 100 | 100 | 100 | [view](docs/screenshots/lighthouse-products-mobile.png) · [before](docs/screenshots/lighthouse-products-mobile-before.png) |
| All products | Desktop | 92 | 100 | 100 | 100 | [view](docs/screenshots/lighthouse-products-desktop.png) |
| Portraits category | Mobile | 81 | 100 | 100 | 100 | [view](docs/screenshots/lighthouse-category-mobile.png) · [before](docs/screenshots/lighthouse-category-mobile-before.png) |
| Portraits category | Desktop | 95 | 100 | 100 | 100 | [view](docs/screenshots/lighthouse-category-desktop.png) |

**What I improved:** the first test showed that pictures were too big ([before](docs/screenshots/lighthouse-before-insights-mobile.png)). Now Cloudinary sends product pictures smaller and in a modern format (`f_auto,q_auto,w_…`), the hero poster has a smaller version for phones, and the icon script loads after the page. This cut the pictures on the home page from about **4,150 KiB to 630 KiB** ([after](docs/screenshots/lighthouse-after-insights-mobile.png)), and desktop performance went from 85 to 91.

Google Fonts now load after the page is shown (`media="print"` with `onload`), so phones show the page sooner. On product lists, the first two pictures load straight away and the rest load when the customer scrolls. Mobile performance went up on every page:

| Page | Mobile before | Mobile after |
|---|---|---|
| Home | 72 | **86** |
| All products | 72 | **74** |
| Portraits category | 73 | **81** |

The All products page shows many large product drawings at once, so it is still a bit slower on mobile. Pages behind a login (bag, checkout, My orders) cannot be tested with PageSpeed, but they use the same base template.

### Accessibility: WAVE

| Page | Errors | Contrast errors | AIM score | Screenshot |
|---|---|---|---|---|
| Home | 0 | 0 | 9.8 / 10 | [view](docs/screenshots/wave-home.png) |
| All products | 0 | 0 | 9.7 / 10 | [view](docs/screenshots/wave-products.png) |

The alerts are a long alt text for the hero drawing (kept on purpose, to describe the picture for screen readers) and "redundant links" (the product picture and the product name both link to the product page, which is normal for shop cards).

### Manual testing

I tested each user story by hand on the live site.

| User story | What I did | Expected | Result |
|---|---|---|---|
| US-01 Register | Registered a new account | Account made, welcome message and email | ✅ |
| US-02 Log in and out | Logged in, then out | Navbar changes, 收工啦 sign after log out | ✅ |
| US-03 Anonymous-only pages | Opened `/accounts/login/` while logged in | Sent to the home page | ✅ |
| US-04 Browse by category | Clicked each category | Only that category's products | ✅ |
| US-05 Product page | Opened a product | Picture, price, description, reviews | ✅ |
| US-07 Add to bag | Added a sticker set | Green message with bag icon, bag count goes up | ✅ |
| US-07 Digital once only | Added the same sticker set again | "Already in your bag", count stays the same | ✅ |
| US-08 Update and remove | Changed a postcard quantity, then removed it | Total updates, item removed, empty bag sign | ✅ |
| US-10 Pay with Stripe | Paid with `4242 4242 4242 4242` | Stripe page, then thank-you page | ✅ |
| US-10 No double click | Clicked Pay twice quickly | Button disabled after the first click | ✅ |
| US-12 Failed payment | Pressed back on the Stripe page | Friendly page, bag kept | ✅ |
| US-13 Webhook | Paid and closed the page at once | Order still marked as paid | ✅ |
| US-14 My orders | Opened My orders | All my orders with status | ✅ |
| US-15 My downloads | Downloaded a ZIP | File downloads, countdown shown | ✅ |
| US-15 Protected download | Opened someone else's download link | 404 page | ✅ |
| US-16 Review | Reviewed a product I bought | Review shows on the product page | ✅ |
| US-16 No review without buying | Opened the review page for a product I did not buy | Error message, no form | ✅ |
| US-17 Edit and delete review | Edited, then deleted my review | Changes show straight away | ✅ |
| US-18 to US-20 Owner products | Added, edited and deleted a product | Shop updates straight away | ✅ |
| US-21 Owner only | Opened `/products/manage/` as a customer | 403 sign page | ✅ |
| US-22 Portrait versions | Chose printed, 3 people | Price €40 + printed price | ✅ |
| US-23 Names and photos | Sent notes and 2 photos | Owner sees them on the order | ✅ |
| US-24 Deliver portrait | Owner uploaded the finished portrait | Email sent, customer can download | ✅ |
| US-35 Shipping | Bought a printed postcard | Shipping method asked, shipping added | ✅ |
| US-36 Owner ships | Owner marked the order as shipped | Shipped email with tracking number | ✅ |
| US-26 Friendly errors | Opened `/abc123/` | 搵唔到 404 sign page | ✅ |
| US-28 Responsive | Checked all pages at phone, tablet and desktop width | Nothing cut off, menu becomes a button on phones | ✅ |

---

## Bugs fixed

| Bug | Cause | Fix |
|---|---|---|
| ZIP downloads showed the 好忙呀 error page on Heroku. Pictures worked. | Cloudinary blocks ZIP and PDF delivery on free accounts by default | Turned on *Allow delivery of PDF and ZIP files* in Cloudinary's security settings |
| Customers who bought a **printed** postcard could also download the file | The download check looked only at the product type, not the version | Added `is_printed=False` to the download checks, with tests |
| W3C: *h3 follows h1* on the shop pages | Product cards use h3, but the page had no h2 | Added a hidden h2 *商品 Products* before the cards |
| W3C: *Article lacks heading* on reviews | Each review was an `<article>` without a heading | The reviewer's name is now the heading |
| JSHint: *Misleading line break before ?* in `cart.js` | A short `? :` written over three lines | Rewrote it as a normal `if / else` |
| The hero picture was broken on Heroku | The new `.webp` file was not added to git | Added the missing files to `static/images` |
| Info messages were Bootstrap blue | Bootstrap's default `alert-info` colour | Info and success messages now use the shop's green |
| The *Being drawn* poster grew out of its card | The `<picture>` wrapper did not fill the box | Added CSS so the picture fits the card |
| Portrait-only orders showed a *My downloads* button | The button checked for any digital item | It now only shows when a file can be downloaded now |
| The 403 page did not show its sign | `{% load static %}` was missing in the template | Added it, with a test |
| Pictures made the mobile site slow | Full-size 1600 × 2000 pictures were sent to small cards | Cloudinary now sends smaller pictures |

---

## Deployment

### Settings in one file

There is only one settings file, `config/settings.py`. It works on my computer and on Heroku, because it reads everything secret or different from **environment variables**:

- On my computer, they come from a `.env` file (not in git)
- On Heroku, they come from the **Config Vars**

The database is set in one place: `DATABASE_URL` (Postgres on Heroku). If it is missing, a local SQLite file is used.

### Environment variables

| Name | What it is |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` only on my computer. Not set on Heroku, so it is off |
| `ALLOWED_HOSTS` | The Heroku address |
| `CSRF_TRUSTED_ORIGINS` | The Heroku address with `https://` |
| `SITE_URL` | The live address, used for links in emails |
| `DATABASE_URL` | Postgres database (added by Heroku) |
| `CLOUDINARY_URL` | Cloudinary account, for product pictures and downloads |
| `STRIPE_SECRET_KEY` | Stripe test secret key |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Gmail SMTP (with a Gmail app password) |
| `DEFAULT_FROM_EMAIL` | The sender name and address for emails |

### Run it on your computer

1. Clone the repository and open the folder:
   ```
   git clone https://github.com/MonicaFeis/moncherie-corner.git
   cd moncherie-corner
   ```
2. Make a virtual environment and install the packages:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Make a `.env` file in the main folder:
   ```
   SECRET_KEY=any-long-random-text
   DEBUG=True
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```
   Without email settings, emails are printed in the terminal.
4. Make the database and an owner account:
   ```
   python3 manage.py migrate
   python3 manage.py createsuperuser
   ```
5. Start the site:
   ```
   python3 manage.py runserver
   ```
6. To test the Stripe webhook on your computer, use the Stripe CLI:
   ```
   stripe listen --forward-to localhost:8000/checkout/webhook/
   ```

### Deploy to Heroku

1. **Create the app** on [Heroku](https://www.heroku.com/): *New → Create new app*.
2. **Add a database:** *Resources → Add-ons → Heroku Postgres*. This adds `DATABASE_URL` automatically.
3. **Cloudinary:** make a free account at [cloudinary.com](https://cloudinary.com/) and copy the *API environment variable* (`CLOUDINARY_URL`). In *Settings → Security*, tick **Allow delivery of PDF and ZIP files**, or downloads will not work.
4. **Stripe:** in the Stripe dashboard (test mode), copy the **secret key**. Under *Developers → Webhooks*, add the endpoint `https://<your-app>.herokuapp.com/checkout/webhook/` with the events `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed` and `checkout.session.expired`, and copy the **signing secret**.
5. **Gmail:** turn on 2-steps verification and make an **app password** for the shop's Gmail address.
6. **Config Vars:** in *Settings → Reveal Config Vars*, add all the variables from the table above. Do not add `DEBUG`.
7. **Connect GitHub:** in *Deploy*, choose GitHub, find `moncherie-corner` and click **Deploy Branch** (or turn on automatic deploys).
8. Heroku installs `requirements.txt`, runs `collectstatic` for the CSS, JavaScript and pictures (served by **WhiteNoise**), and the `Procfile` runs `migrate` before starting **gunicorn**:
   ```
   release: python manage.py migrate --noinput
   web: gunicorn config.wsgi
   ```
9. **Make the owner account** on Heroku: *More → Run console*, then `python manage.py createsuperuser`.
10. Log in to `/admin/`, add the categories, shipping methods and products.

Static files are served by WhiteNoise, and uploaded files (product pictures and downloads) are stored on Cloudinary, because Heroku deletes uploaded files every time the app restarts. AWS S3 is not needed.

**Checking the deployed version:** after each deploy, I clicked through the live site (shop, bag, checkout with the test card, downloads, owner pages) and checked that it works the same as on my computer.

Payments use Stripe in test mode (a sandbox), so no real money is taken. A real shop would need a registered business and a fully activated Stripe account.

---

## Technologies

- **Languages:** Python 3.14, HTML, CSS, JavaScript
- **Framework:** Django 6.1
- **Database:** PostgreSQL (Heroku), SQLite (local)
- **Front end:** Bootstrap 5.3, Font Awesome icons, Google Fonts
- **Payments:** Stripe Checkout and webhooks
- **Files:** Cloudinary (uploads), WhiteNoise (static files)
- **Hosting:** Heroku, with gunicorn
- **Email:** Gmail SMTP
- **Tools:** Git and GitHub, VS Code, flake8, Procreate (drawings)
- **Testing tools:** Django test framework, W3C HTML and CSS validators, JSHint, Lighthouse, WAVE

---

## Credits

### Artwork

- **All drawings are my own**: the stickers, postcards, portraits, the hero poster and all the shop signs, drawn in Procreate.
- The website art products (floor tiles, mosaic tiles, Old Shanghai frames) are inspired by old Hong Kong and Shanghai design.

### Code and help

- [Django documentation](https://docs.djangoproject.com/), for models, forms, authentication and testing
- [Stripe documentation](https://docs.stripe.com/), for Checkout and webhooks
- [Bootstrap 5 documentation](https://getbootstrap.com/), for the grid, navbar and alerts
- [Cloudinary](https://cloudinary.com/documentation) and [WhiteNoise](https://whitenoise.readthedocs.io/) documentation
- Code Institute course material, for the structure of a Django e-commerce project and deployment to Heroku


### Fonts and icons

- [Noto Serif TC, Noto Sans TC and Playball](https://fonts.google.com/) from Google Fonts
- Icons from [Font Awesome](https://fontawesome.com/)

### Thanks

Thank you to Code Institute for the feedback.
