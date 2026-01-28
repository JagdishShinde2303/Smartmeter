# Smart Energy Meter Billing Service

Automated billing module for computing energy charges based on tariff slabs, generating invoices, and sending emails.

## Features

- ✅ Slab-based tariff calculation (0-100, 101-300, 301+ kWh)
- ✅ Configurable fixed charges and taxes (GST)
- ✅ PDF invoice generation
- ✅ Email delivery to customers
- ✅ Monthly billing cron job (1st of month at 00:05)
- ✅ Invoice storage in MongoDB
- ✅ Retry logic for failed emails
- ✅ Comprehensive logging

## Project Structure

```
billing/
├── src/
│   ├── billingJob.js          # Main cron job scheduler
│   ├── billingService.js      # Core billing logic
│   ├── invoiceGenerator.js    # PDF creation
│   ├── emailService.js        # SMTP email delivery
│   ├── tariffConfig.js        # Tariff slab definitions
│   ├── models/
│   │   └── invoiceSchema.js
│   └── scripts/
│       └── generateInvoice.js # Manual invoice generation
├── package.json
├── README.md
└── templates/
    └── invoice-template.html  # HTML email template
```

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# In root .env or billing/.env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/smartmeter
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-specific-password  # Use Gmail app password, not account password
SMTP_FROM=billing@smartmeter.local
TIMEZONE=Asia/Kolkata
BILLING_CRON_SCHEDULE=0 5 1 * *     # 00:05 on 1st of month
```

### 3. Start Billing Service

```bash
npm run dev
```

Monitor output for job execution logs.

## Core Modules

### billingService.js

Computes monthly bill for a device:

```javascript
const bill = await computeBill(deviceId, '2026-01');
// Returns: {
//   device_id,
//   month,
//   energy_kwh,
//   slabs: [{ slab, units, rate, charge }, ...],
//   subtotal,
//   fixed_charge,
//   tax,
//   total
// }
```

### invoiceGenerator.js

Generates PDF invoice using PDFKit:

```javascript
const pdfBuffer = await generateInvoicePDF(billData, userInfo);
// Save to file or upload to S3
fs.writeFileSync(`invoice-${deviceId}-${month}.pdf`, pdfBuffer);
```

### emailService.js

Sends invoice email to customer:

```javascript
await sendInvoiceEmail({
  to: 'customer@example.com',
  deviceId: 'meter-001',
  month: '2026-01',
  invoiceUrl: 'https://s3.../invoice.pdf'
});
```

### tariffConfig.js

Defines tariff slabs and rates:

```javascript
const tariffConfig = {
  slabs: [
    { range: "0-100", rate: 3.50 },
    { range: "101-300", rate: 4.50 },
    { range: "301+", rate: 6.00 }
  ],
  fixed_charge: 50,              // ₹50/month
  tax_rate: 0.18,                // 18% GST
  currency: "INR",
  minimum_bill: 50               // Minimum charge
};
```

## Billing Calculation Example

**Scenario:**
- Device consumed 250 kWh in January 2026
- Tariff slabs: 0-100 @ ₹3.50, 101-300 @ ₹4.50, 301+ @ ₹6.00
- Fixed charge: ₹50
- Tax: 18% GST

**Calculation:**

```
Units in Slab 0-100:    100 × 3.50 = ₹350
Units in Slab 101-300:  150 × 4.50 = ₹675
                        ───────────
Subtotal (slab charge):            ₹1,025

Fixed charge:                       ₹50
Subtotal with fixed:               ₹1,075

Tax (18% GST):    1075 × 0.18 =    ₹193.50
                                   ───────
Total Bill:                        ₹1,268.50
```

## Cron Job Execution

The billing job runs at **00:05 on the 1st of each month**:

```javascript
const cronSchedule = '0 5 1 * *';  // Crontab format
// Minute: 0 (start of hour)
// Hour: 5 (5 AM)
// Day: 1 (1st day)
// Month: * (every month)
// DayOfWeek: * (every day of week)
```

### Job Steps:

1. Fetch all active devices from MongoDB
2. For each device:
   - Query energy consumption for previous month
   - Compute bill using tariff slabs
   - Create invoice document in MongoDB
   - Generate PDF
   - Send email to customer
   - Log outcome
3. Report summary (e.g., "250 invoices generated, 10 emails failed")

## Manual Invoice Generation

Generate invoice on-demand:

```bash
node src/scripts/generateInvoice.js --device=meter-001 --month=2026-01
```

Output:

```
Generated invoice for meter-001 (January 2026)
Total: ₹1,268.50
PDF saved: invoices/meter-001-2026-01.pdf
Email sent to: customer@example.com
```

## Invoice Data Model

```javascript
// MongoDB invoices collection
{
  _id: ObjectId,
  device_id: "meter-001",
  month: "2026-01",
  energy_kwh: 250,
  slabs: [
    { range: "0-100", units: 100, rate: 3.50, charge: 350 },
    { range: "101-300", units: 150, rate: 4.50, charge: 675 }
  ],
  subtotal: 1025,
  fixed_charge: 50,
  tax: 193.50,
  total: 1268.50,
  currency: "INR",
  status: "issued",        // issued | paid | overdue
  pdf_url: "s3://invoices/meter-001-2026-01.pdf",
  email_status: "sent",    // sent | failed | pending
  email_to: "customer@example.com",
  created_at: ISODate("2026-02-01T05:05:00Z"),
  due_date: ISODate("2026-02-15"),
  paid_date: null,
  notes: ""
}
```

## Email Template

Invoice email includes:

```
Subject: Smart Meter Invoice - meter-001 (January 2026)

Dear Customer,

Your energy bill for January 2026 is ready.

Device: meter-001 (Flat-101)
Period: 01 Jan – 31 Jan 2026
Consumption: 250 kWh

BILL SUMMARY
───────────────────
Slab 0-100 kWh:   100 × ₹3.50 = ₹350
Slab 101-300 kWh: 150 × ₹4.50 = ₹675
Fixed charge:               ₹50
───────────────────
Subtotal:                   ₹1,075
Tax (18% GST):             ₹193.50
═══════════════════
TOTAL DUE: ₹1,268.50

Due Date: 15 Feb 2026
Status: Unpaid

Download PDF: [Link to PDF]
Pay Now: [Payment link]

---
Smart Energy Meter Billing System
Contact: support@smartmeter.local
```

## Configuration Examples

### Example 1: Residential (India)

```javascript
const residentialTariff = {
  slabs: [
    { range: "0-100", rate: 3.50 },
    { range: "101-300", rate: 4.50 },
    { range: "301+", rate: 6.00 }
  ],
  fixed_charge: 50,
  tax_rate: 0.18,
  minimum_bill: 50
};
```

### Example 2: Commercial (USA)

```javascript
const commercialTariff = {
  slabs: [
    { range: "0-500", rate: 0.12 },
    { range: "501-2000", rate: 0.10 },
    { range: "2001+", rate: 0.08 }
  ],
  fixed_charge: 30,
  demand_charge: 15,  // $/kW
  tax_rate: 0.0875,   // 8.75%
  currency: "USD"
};
```

### Example 3: Time-of-Use (TOU)

```javascript
const touTariff = {
  periods: {
    peak: { hours: "9-21", rate: 6.00 },
    offpeak: { hours: "21-9", rate: 3.00 }
  },
  fixed_charge: 80,
  tax_rate: 0.18
};
```

## Retry Logic

Failed email sends are retried with exponential backoff:

```javascript
// Retry configuration
const retryConfig = {
  maxRetries: 3,
  baseDelay: 5000,       // 5 seconds
  backoffMultiplier: 2   // 5s, 10s, 20s
};
```

## Testing

```bash
npm test
```

Test cases include:
- Slab calculation accuracy
- PDF generation and formatting
- Email delivery with mocks
- Cron job scheduling
- Edge cases (zero consumption, minimum charges, taxes)

## Production Checklist

- ✅ Verify tariff slabs match regulatory requirements
- ✅ Test email delivery with sample invoices
- ✅ Confirm PDF format and branding
- ✅ Set correct timezone in cron schedule
- ✅ Enable audit logging for all billing operations
- ✅ Configure backup for invoice storage
- ✅ Test retry logic and error handling
- ✅ Document tariff changes in changelog
- ✅ Set up alerting for failed billing jobs

## Monitoring

### Health Check

```bash
curl http://localhost:5000/health/billing
```

Response:

```json
{
  "status": "ok",
  "last_run": "2026-02-01T05:05:30Z",
  "invoices_generated": 245,
  "emails_sent": 245,
  "emails_failed": 0,
  "next_run": "2026-03-01T05:05:00Z"
}
```

### Logs

Monitor billing job logs in Winston logger:

```
[INFO] 2026-02-01 05:05:00 Billing job started
[INFO] 2026-02-01 05:05:05 Processing device: meter-001
[INFO] 2026-02-01 05:05:06 Bill computed: ₹1,268.50
[INFO] 2026-02-01 05:05:07 PDF generated
[INFO] 2026-02-01 05:05:08 Email sent to customer@example.com
...
[INFO] 2026-02-01 05:15:00 Billing job completed
[INFO] Generated: 245 invoices, Sent: 245 emails, Failed: 0
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cron job never runs | Check system time, verify cron format, inspect logs |
| Email delivery fails | Verify SMTP credentials, check Gmail app password, inspect firewall |
| PDF generation errors | Check disk space, verify PDFKit installation, enable debug logs |
| Incorrect bill calculation | Verify tariff config, check energy aggregation query, inspect DB data |

## Next Steps

1. **Sprint 1:** Define tariff config, test slab calculation
2. **Sprint 2:** Implement PDF generation with proper branding
3. **Sprint 3:** Set up SMTP and test email delivery
4. **Sprint 4:** Deploy cron job to production and monitor
5. **Sprint 5:** Add dashboard for invoice history and payment tracking

---

See main [README.md](../README.md) for full project overview.
