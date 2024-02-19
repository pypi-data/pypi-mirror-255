## Description

Welcome to thnkrAI’s Pricing Model and SDK documentation.

thnkrAI allows you to conduct detailed pricing analysis on any kind of product or product datasets you want in an easy and accessible way. thnkrAI’s pricing model can bring enabling price predictions, discovery, and insights to your data.

Use the thnkrAI SDK to quickly read product information and predict prices using the model’s price prediction endpoint.

## Model Overview

thnkrAI’s General Pricing Model

**Model Description:** Text-to-Price Model takes in product data from everyday consumer products and predicts an estimated price based on that information.

**Model Type:** Natural Language Processing (NLP); Regression Model

**Model Input:** String of product data (title/description)

**Model Output:** Numerical float as the predicted price ($USD)

**Key Features:** Natural Language Processing, Character vectorization, Regression.

**Model Evaluation:** Evaluated using Mean Absolute Percentage Error (MAPE), R-Squared (R2), and Mean Squared Error (MSE).

## Installation

```python
!pip install thnkrSDK
```

## thnkrSDK Integration

### `LICENSE: MIT`

```python
import thnkrSDK as thnkr

username = "YOUR_USERNAME"
password = "YOUR_PASSWORD"

model = "general_v1"
product_title = "EXAMPLE_TEXT"

prediction = thnkr.predict(model, product_title, username, password)
```

Example Output:

```json
55.49
```

## Contact Information

- **Contact** the thnkrAI team at [contact@thnkrai.com](mailto:contact@thnkrai.com) with any questions or concerns

## Model Limitations

- Model is currently trained on limited text data from products listed online. The products come from one online ecommerce marketplace, meaning products found on other marketplaces may be interpreted differently by the model. We are currently working on collecting more product data from a multitude of various online sources to combat this issue.
- If the product data input is not descriptive enough or lacks substantial detail, the model may return inaccurate price predictions compared to those with substantial detail. To combat this, we are working on training the model with more diverse lengths of input strings.

## Support

- If you have any issues or questions please contact us at contact@thnkrai.com

## Version History

- Trained November 15, 2023: thnkrAI general_v1

## Base URL

- `https://api.thnkrai.com`

## Parameters

```python
thnkr.predict('model', 'data_input', 'username', 'password')
```

## Errors

This API uses the following error codes:

- `200 Successful Request`: The request was malformed or missing required parameters.
- `400 Bad Request`: The request was malformed or missing required parameters.
- `401 Unauthorized`: The API key provided was invalid or missing.
- `404 Not Found`: The requested resource was not found.
- `500 Internal Server Error`: An unexpected error occurred on the server.