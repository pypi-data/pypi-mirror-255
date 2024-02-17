from datetime import datetime

class Transformations:
    def __init__(self, date_formats):
        self.date_formats = date_formats

    def transform_date(self, date_str):
        for date_format in self.date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                transformed_date = parsed_date.strftime("%B %d, %Y")
                return transformed_date
            except ValueError:
                continue
        raise ValueError('Invalid date format')

    def transform_timestamp(self, timestamp):
        try:
            timestamp = float(timestamp)
            transformed_datetime = datetime.utcfromtimestamp(timestamp)
            return transformed_datetime.strftime("%Y-%m-%d %H:%M:%S UTC")
        except ValueError:
            raise ValueError('Invalid timestamp format')

    def transform_currency(self, amount):
        try:
            amount = float(amount)
            # Assuming Tunisian Dinar (TND) currency
            transformed_amount = "{:,.3f} TND".format(amount)
            return transformed_amount
        except ValueError:
            raise ValueError('Invalid currency format')


    def transform_percentage(self, percentage):
        try:
            percentage = float(percentage)
            transformed_percentage = "{:.2%}".format(percentage)
            return transformed_percentage
        except ValueError:
            raise ValueError('Invalid percentage format')

    def transform_uppercase(self, text):
        try:
            transformed_text = text.upper()
            return transformed_text
        except AttributeError:
            raise ValueError('Invalid text format for uppercase transformation')

    def transform_lowercase(self, text):
        try:
            transformed_text = text.lower()
            return transformed_text
        except AttributeError:
            raise ValueError('Invalid text format for lowercase transformation')

    def transform_boolean(self, value):
        try:
            return bool(value)
        except ValueError:
            raise ValueError('Invalid boolean format')

    def transform_integer(self, value):
        try:
            return int(value)
        except ValueError:
            raise ValueError('Invalid integer format')

    def transform_float(self, value):
        try:
            return float(value)
        except ValueError:
            raise ValueError('Invalid float format')

    def transform_age_category(self, age):
        try:
            age = int(age)
            if 0 <= age < 18:
                return 'Underage'
            elif 18 <= age < 65:
                return 'Adult'
            else:
                return 'Senior'
        except ValueError:
            raise ValueError('Invalid age format')

    def transform_phone_number(self, phone_number):
        try:
            return f"+216 {phone_number[:2]} {phone_number[2:5]} {phone_number[5:8]} {phone_number[8:]}"
        except (ValueError, IndexError):
            raise ValueError('Invalid phone number format')

    def transform_email_redaction(self, email):
        # Redact part of the email address for privacy (e.g., replace characters with asterisks)
        parts = email.split("@")
        if len(parts) == 2:
            username, domain = parts
            redacted_username = username[0] + "*" * (len(username) - 1)
            return f"{redacted_username}@{domain}"
        else:
            return email

    def transform_mask_credit_card(self, credit_card_number):
        if len(credit_card_number) >= 16:
            masked_number = credit_card_number[:6] + "*" * 8 + credit_card_number[-4:]
            return masked_number
        else:
            raise ValueError('Invalid credit card number format')

    def transform_truncate_text(self, text, max_length=50):
        if len(text) > max_length:
            truncated_text = text[:max_length] + "..."
            return truncated_text
        else:
            return text

    def transform_reverse_string(self, text):
        # Reverse the characters in a string
        return text[::-1]

    def transform_strip_whitespace(self, text):
        # Remove leading and trailing whitespaces from a string
        return text.strip()


