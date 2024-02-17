import json
from datetime import datetime
from datetime import timedelta

import cloudscraper
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer
from pydantic import field_validator
from tenacity import retry

default_timeout = 10


class OriginalValues(BaseModel):
    from_currency: str = Field(validation_alias="fromCurrency")
    from_currency_name: str = Field(validation_alias="fromCurrencyName")
    to_currency: str = Field(validation_alias="toCurrency")
    to_currency_name: str = Field(validation_alias="toCurrencyName")
    as_of_date: datetime = Field(validation_alias="asOfDate")
    from_amount: float = Field(validation_alias="fromAmount")
    to_amount_with_visa_rate: float = Field(validation_alias="toAmountWithVisaRate")
    to_amount_with_additional_fee: float = Field(validation_alias="toAmountWithAdditionalFee")
    fx_rate_visa: float = Field(validation_alias="fxRateVisa")
    fx_rate_with_additional_fee: float = Field(validation_alias="fxRateWithAdditionalFee")
    last_updated_visa_rate: datetime = Field(validation_alias="lastUpdatedVisaRate")
    benchmarks: list = Field(validation_alias="benchmarks")

    @field_validator("as_of_date", "last_updated_visa_rate", mode="before")
    @classmethod
    def validate_datetime(cls, v: int) -> datetime:
        return datetime.fromtimestamp(v)

    @field_validator(
        "from_amount",
        "to_amount_with_visa_rate",
        "to_amount_with_additional_fee",
        "fx_rate_visa",
        "fx_rate_with_additional_fee",
        mode="before",
    )
    @classmethod
    def validate_float(cls, v: str) -> float:
        if v == "":
            return 0

        return float(v)


class RateResponse(BaseModel):
    original_values: OriginalValues = Field(validation_alias="originalValues")
    conversion_amount_value: float = Field(validation_alias="conversionAmountValue")
    conversion_bank_fee: float = Field(validation_alias="conversionBankFee")
    conversion_input_date: datetime = Field(validation_alias="conversionInputDate")
    conversion_from_currency: str = Field(validation_alias="conversionFromCurrency")
    conversion_to_currency: str = Field(validation_alias="conversionToCurrency")
    from_currency_name: str = Field(validation_alias="fromCurrencyName")
    to_currency_name: str = Field(validation_alias="toCurrencyName")
    converted_amount: float = Field(validation_alias="convertedAmount")
    bench_mark_amount: str = Field(validation_alias="benchMarkAmount")
    fx_rate_with_additional_fee: float = Field(validation_alias="fxRateWithAdditionalFee")
    reverse_amount: float = Field(validation_alias="reverseAmount")
    disclaimer_date: datetime = Field(validation_alias="disclaimerDate")
    status: str = Field(validation_alias="status")

    @field_validator("conversion_input_date", mode="before")
    @classmethod
    def validate_conversion_input_date(cls, v: str) -> datetime:
        return datetime.strptime(v, "%m/%d/%Y")

    @field_validator("disclaimer_date", mode="before")
    @classmethod
    def validate_disclaimer_date(cls, v: str) -> datetime:
        return datetime.strptime(v, "%B %d, %Y")

    @field_validator(
        "conversion_amount_value",
        "conversion_bank_fee",
        "converted_amount",
        "fx_rate_with_additional_fee",
        "reverse_amount",
        mode="before",
    )
    @classmethod
    def validate_float(cls, v: str) -> float:
        if v == "":
            return 0

        return float(v)


class RateRequest(BaseModel):
    amount: float
    from_curr: str = Field(serialization_alias="fromCurr")
    to_curr: str = Field(serialization_alias="toCurr")
    fee: float = Field(default=0.0)
    utc_converted_date: datetime = Field(default_factory=datetime.utcnow, serialization_alias="utcConvertedDate")
    exchangedate: datetime = Field(default_factory=datetime.utcnow, serialization_alias="exchangedate")

    @field_serializer("exchangedate", "utc_converted_date")
    def validate_date(self, d: datetime) -> str:
        return d.strftime("%m/%d/%Y")

    def do(self) -> RateResponse:
        url = "http://www.visa.com.tw/cmsapi/fx/rates"

        scraper = cloudscraper.create_scraper()

        resp = scraper.get(url=url, params=self.model_dump(by_alias=True), timeout=default_timeout)

        return RateResponse(**resp.json())


@retry
def query_rate(
    amount: float = 1,
    from_curr: str = "TWD",
    to_curr: str = "USD",
    fee: float = 0,
    date: datetime = None,
) -> RateResponse:
    if date is None:
        date = datetime.now()

    try:
        resp = RateRequest(
            amount=amount,
            from_curr=from_curr,
            to_curr=to_curr,
            fee=fee,
            date=date,
        ).do()
    except json.decoder.JSONDecodeError:
        resp = RateRequest(
            amount=amount,
            from_curr=from_curr,
            to_curr=to_curr,
            fee=fee,
            date=date - timedelta(days=1),
        ).do()

    return resp
