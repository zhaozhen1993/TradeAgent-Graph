from langchain_core.tools import tool

# --- 模拟物流计费规则 ---
MOCK_SHIPPING_RATES = {
    "US": {"sea_days": "25-30天", "sea_price_per_kg": 1.5, "air_days": "5-7天", "air_price_per_kg": 6.5},
    "UK": {"sea_days": "30-35天", "sea_price_per_kg": 1.8, "air_days": "6-8天", "air_price_per_kg": 7.0},
    "DE": {"sea_days": "30-35天", "sea_price_per_kg": 1.7, "air_days": "6-8天", "air_price_per_kg": 6.8},
}

@tool
def estimate_shipping_cost(destination_country_code: str, weight_kg: float, method: str = "sea") -> str:
    """
    估算发往指定国家的物流运费和时效。
    输入参数：
    - destination_country_code (字符串): 国家代码，如 "US", "UK", "DE"。
    - weight_kg (浮点数): 货物总重量（公斤）。
    - method (字符串): 运输方式，"sea" 代表海运，"air" 代表空运。默认为海运。
    """

    country_code = destination_country_code.upper()
    rates = MOCK_SHIPPING_RATES.get(country_code, {})

    if not rates:
        return f"抱歉，暂不支持查询发往 {destination_country_code} 的运费，请确认国家代码是否正确。"

    if method.lower() == "sea":
        price_per_kg = rates["sea_price_per_kg"]
        days = rates["sea_days"]
        method_name = "海运"
    else:
        price_per_kg = rates["air_price_per_kg"]
        days = rates["air_days"]
        method_name = "空运"

    total_cost = price_per_kg * weight_kg
    return (f"发往 {country_code} 的 {weight_kg}kg 货物，选择【{method_name}】方式：\n"
            f"预估运费：{total_cost:.2f} USD\n"
            f"预估时效：{days}\n"
            f"*(注：此费用仅为预估，最终运费以实际出货账单为准)*")

logistics_tools = [estimate_shipping_cost]