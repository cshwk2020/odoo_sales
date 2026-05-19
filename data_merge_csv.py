import pandas as pd

# 讀取 CSV
df = pd.read_csv("/Volumes/linuxkernel/PY3.10_BASE/product_samples/listing.csv")

# 按 default_code 分組，數值欄位累加
merged = df.groupby(
    ["default_code", "name", "list_price", "standard_price", "categ_id", "uom_id"],
    as_index=False
).agg({
    "On Hand": "sum",
    "Incoming Qty": "sum",
    "Outgoing Qty": "sum",
    "Forecasted": "sum"
})

# 輸出新 CSV
merged.to_csv("/Volumes/linuxkernel/PY3.10_BASE/product_samples/listing_merged.csv", index=False)
print("Merged CSV saved as listing_merged.csv")