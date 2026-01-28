import pandas as pd
try:
    data = ['2025-12-01 17:52:03', '2025-10-15']
    print(f"Testing mixed list: {data}")
    res = pd.to_datetime(data)
    print("Result:", res)
except Exception as e:
    print("Caught error on simple list mixed:", e)

print("\nTesting mixed list with errors='coerce':")
res_coerce = pd.to_datetime(data, errors='coerce')
print("Result coerce:", res_coerce)
