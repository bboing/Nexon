#!/usr/bin/env python3
"""
파싱 테스트
"""

response = """[THOUGHT]
"아이스진"이 무엇인지, 어디서 살 수 있는지 검색해야겠다.

[ACTION]
{"action_type": "search", "query": "아이스진", "category": null}
"""

import json

# ACTION 파싱
if "[ACTION]" in response:
    action_part = response.split("[ACTION]", 1)[1].strip()
    print(f"Action part: {repr(action_part)}")
    
    if "{" in action_part and "}" in action_part:
        start = action_part.index("{")
        end = action_part.rindex("}") + 1
        json_str = action_part[start:end]
        print(f"JSON string: {repr(json_str)}")
        
        try:
            action_data = json.loads(json_str)
            print(f"✅ Parsed: {action_data}")
        except json.JSONDecodeError as e:
            print(f"❌ Parse error: {e}")
