# 🔧 Phase 2 Implementation Guide

## What We Need to Complete Auto-Booking

This document tracks what information we need to capture to implement **Phase 2: Automatic Payment & Booking**.

---

## 📋 Information Needed

### ✅ What We Already Have

1. **API Endpoints (Working)**
   - `GET /Setup` ✓
   - `POST /AvailabilityForDateRange` ✓
   - `GET /AvailabilitySearch` ✓

2. **Stripe Integration Confirmed**
   ```json
   "StripePublishableKey": "pk_live_6G2ASZKBTJJNEtJROnpmRSt6"
   ```

3. **Payment Policy**
   - 50€ per person deposit
   - Deducted from final bill
   - Charged for no-show or late cancellation

---

## ❓ What We Need to Capture

### 1. Booking Endpoint

**What to capture:**
```
POST https://booking.resdiary.com/api/Restaurant/TRATTORIATRIPPA/???
```

**Possible endpoints:**
- `/CreateBooking`
- `/Booking`
- `/MakeReservation`
- `/Reserve`
- `/CompleteBooking`

**How to find:**
1. Open DevTools → Network tab
2. Filter: XHR/Fetch
3. Select available slot
4. Fill in form with test data
5. Click final "Confirm" button
6. Look for POST request

---

### 2. Booking Payload Structure

**What to capture:**

```json
{
  // CONFIRMED FIELDS (we know these)
  "Date": "2026-04-15",
  "Time": "20:30", 
  "Covers": 2,
  "FirstName": "Mario",
  "LastName": "Rossi",
  "Email": "mario@example.com",
  "PhoneNumber": "+393201234567",
  "ChannelCode": "INGLESE",
  
  // UNKNOWN FIELDS (need to capture)
  "PaymentToken": "???",           // Stripe token
  "DepositAmount": ???,            // 100.00 for 2 people?
  "AreaId": ???,                   // Optional area preference?
  "AcceptTerms": ???,              // true/false?
  "MarketingConsent": ???,         // true/false?
  "SpecialRequests": ???,          // Optional notes?
  "???": "???"                     // Any other fields?
}
```

**How to find:**
1. In Network tab, find the POST request
2. Click on it → "Payload" tab
3. Copy the entire JSON structure

---

### 3. Stripe Payment Flow

**What to capture:**

We need to know EXACTLY how Stripe is called before the booking:

**Option A: stripe.createToken()**
```javascript
stripe.createToken({
  card: {
    number: '4242424242424242',
    exp_month: 12,
    exp_year: 2026,
    cvc: '123'
  }
})
// Returns: {token: {id: "tok_xxxxx"}}
```

**Option B: stripe.createPaymentMethod()**
```javascript
stripe.createPaymentMethod({
  type: 'card',
  card: cardElement,
  billing_details: {...}
})
// Returns: {paymentMethod: {id: "pm_xxxxx"}}
```

**Option C: stripe.confirmCardPayment()**
```javascript
stripe.confirmCardPayment(clientSecret, {
  payment_method: {...}
})
```

**How to find:**
1. Network tab → Look for requests to `api.stripe.com`
2. Check request payload and response
3. Note the method used (`/v1/tokens` vs `/v1/payment_methods`)

---

### 4. Request Headers

**What to capture:**

Sometimes special headers are needed:

```
Content-Type: application/json
X-Requested-With: XMLHttpRequest
X-CSRF-Token: ???
Authorization: ???
Cookie: ???
```

**How to find:**
1. In Network tab → POST request
2. "Headers" tab
3. Copy all request headers

---

### 5. Response Structure

**What to capture:**

Success response:
```json
{
  "success": true,
  "confirmationCode": "ABC123",
  "bookingId": 12345,
  "message": "Booking confirmed",
  ???
}
```

Error response:
```json
{
  "success": false,
  "error": "...",
  "errorCode": "...",
  ???
}
```

**How to find:**
1. Network tab → POST request
2. "Response" tab
3. Copy the JSON

---

## 🎯 Step-by-Step Capture Guide

### When a Slot Becomes Available:

**1. Prepare Chrome DevTools**
```
1. Open Chrome
2. Go to https://www.trippamilano.it/book-a-table-2/
3. Cmd+Opt+I (open DevTools)
4. Network tab
5. Check "Preserve log"
6. Filter: XHR/Fetch
```

**2. Start Booking Process**
```
1. Select available date
2. Select available time
3. Click "Next" or "Continue"
```

**3. Fill Form (Use Test Card)**
```
Personal Data:
- First Name: Mario
- Last Name: Test
- Email: test@example.com  
- Phone: +393201234567

Stripe Test Card:
- Number: 4242 4242 4242 4242
- Exp: 12/26
- CVC: 123
```

**4. Before Clicking Final Confirm**
```
1. Check Network tab
2. You should already see Stripe calls
3. Note the stripe.com requests
```

**5. Click Confirm**
```
1. Click final "Confirm Booking" button
2. Watch Network tab for POST request
3. DON'T CLOSE THE TAB YET
```

**6. Capture Everything**
```
For each request (Stripe + ResDiary):
1. Right-click → Copy → Copy as cURL
2. Paste into a text file
3. Also copy request/response JSON
```

**7. Save All Data**
```
Create a file: booking_capture.txt

Include:
- All cURL commands
- Request payloads (JSON)
- Response payloads (JSON)  
- Screenshots of Network tab
- Any error messages
```

---

## 💻 Implementation Plan (After Capture)

Once we have the data, implementation will be:

### 1. Update `src/api/resdiary_client.py`

```python
def book_table(self, ...):
    # Step 1: Create Stripe token
    stripe_token = self._create_stripe_token(card_data)
    
    # Step 2: Call ResDiary booking endpoint
    payload = {
        "Date": date,
        "Time": time,
        # ... exact structure from capture
        "PaymentToken": stripe_token
    }
    
    response = self.session.post(EXACT_ENDPOINT, json=payload)
    return response.json()
```

### 2. Add Stripe Client

```python
# New file: src/payment/stripe_client.py
class StripeClient:
    def create_token(self, card_number, exp_month, exp_year, cvc):
        # Use Stripe Python library
        import stripe
        stripe.api_key = "sk_test_..."  # From config
        
        token = stripe.Token.create(
            card={
                "number": card_number,
                "exp_month": exp_month,
                "exp_year": exp_year,
                "cvc": cvc
            }
        )
        return token.id
```

### 3. Update Configuration

```python
# config/settings.py
PAYMENT_CONFIG = {
    "card_number": os.getenv("CARD_NUMBER"),
    "exp_month": os.getenv("CARD_EXP_MONTH"),
    "exp_year": os.getenv("CARD_EXP_YEAR"),
    "cvc": os.getenv("CARD_CVC"),
}
```

### 4. Security

```bash
# Use .env file (never commit to git!)
CARD_NUMBER=4111111111111111
CARD_EXP_MONTH=12
CARD_EXP_YEAR=2026
CARD_CVC=123
```

---

## ⚠️ Important Notes

### Test Card Numbers (Stripe)

Use these for testing (they don't charge):
```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0027 6000 3184
```

### Don't Worry About:
- The test booking won't actually reserve a table
- Stripe test cards are safe to use
- You can cancel before final submission if worried

### Do Worry About:
- Capturing the EXACT payload structure
- All required fields
- Correct endpoint URL
- Request headers

---

## 📞 Questions to Answer During Capture

- [ ] What's the exact booking endpoint URL?
- [ ] What Stripe method is used? (token, payment_method, etc.)
- [ ] Is there a clientSecret from ResDiary?
- [ ] Are there any CSRF tokens?
- [ ] What's the exact payment amount field name?
- [ ] Are there any hidden form fields?
- [ ] What happens if you use an invalid card?
- [ ] Is there 3D Secure authentication required?

---

## 🎉 Once Complete

After capturing everything, send me:
1. `booking_capture.txt` with all cURLs and JSON
2. Screenshots of Network tab
3. Any notes about the process

Then I'll implement Phase 2 in ~30 minutes! 🚀

---

**Current Status: PHASE 1 COMPLETE ✓**
**Next: Waiting for booking capture data**
