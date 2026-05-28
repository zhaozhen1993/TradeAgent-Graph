from langchain_core.tools import tool
from .knowledge import search_knowledge_base
# 实际开发中，这里应该是调用你的 ERP 或 WMS 系统的 API 接口
MOCK_INVENTORY_DB = {
    "SKU001": {"name": "男士纯棉T恤", "stock": 5000, "base_price": 5.50, "currency": "USD"},
    "SKU002": {"name": "女士瑜伽裤", "stock": 1200, "base_price": 8.00, "currency": "USD"},
    "SKU003": {"name": "户外运动水杯", "stock": 0, "base_price": 3.20, "currency": "USD"}, # 缺货商品
}

@tool
def check_stock(product_sku:str):
    """
    查询指定 SKU 的实时库存数量。
    输入参数：product_sku (字符串)，例如 "SKU001"。
    """
    product = MOCK_INVENTORY_DB.get(product_sku)
    if not product:
        return f"未找到 SKU 为 {product_sku} 的产品信息。"

    if product["stock"] > 0:
        return f"产品 {product['name']} ({product_sku}) 当前库存充足，剩余 {product['stock']} 件。"
    else:
        return f"抱歉，产品 {product['name']} ({product_sku}) 当前暂时缺货。"

@tool
def get_tiered_price(product_sku: str, quantity: int):
    """
    根据采购数量计算阶梯报价（外贸常见需求）。
    输入参数：product_sku (字符串) 和 quantity (整数，采购数量)。
    """
    product = MOCK_INVENTORY_DB.get(product_sku)
    if not product:
        return f"未找到 SKU 为 {product_sku} 的产品信息。"

    base_price = product["base_price"]

    # 外贸阶梯定价逻辑：买得越多越便宜
    if quantity >= 1000:
        final_price = base_price * 0.85  # 95折
        tier = "1000+ (享受85折)"
    elif quantity >= 500:
        final_price = base_price * 0.90  # 9折
        tier = "500-999 (享受9折)"
    elif quantity >= 100:
        final_price = base_price * 0.95  # 95折
        tier = "100-499 (享受95折)"
    else:
        final_price = base_price
        tier = "< 100 (原价)"

    total_price = final_price + quantity

    return (f"产品 {product['name']} ({product_sku}) 采购 {quantity} 件，"
            f"适用阶梯：{tier}。单价：{final_price:.2f} {product['currency']}，"
            f"总价预估：{total_price:.2f} {product['currency']}。")

sales_tools = [check_stock, get_tiered_price,search_knowledge_base]
