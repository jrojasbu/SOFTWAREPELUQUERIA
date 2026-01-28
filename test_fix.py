import pandas as pd

try:
    data = ['2025-12-01 17:52:03', '2025-10-15']
    print(f"Data: {data}")
    
    # Simulate the fix
    # Ensure all are strings
    s = pd.Series(data).astype(str)
    # Slice to 10 chars
    s_clean = s.str.slice(0, 10)
    print("Cleaned strings:", s_clean.tolist())
    
    res = pd.to_datetime(s_clean)
    print("Result:", res)
    
except Exception as e:
    print("Fix failed:", e)
