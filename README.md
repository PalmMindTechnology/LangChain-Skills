agent_skills/
│
├── app/
│   ├── main.py
│   ├── agent/
│   │   ├── builder.py
│   │   ├── executor.py
│   │   └── skill_loader.py
│   │
│   ├── skills/
│   │   ├── registry.py
│   │   │
│   │   ├── sql_skill/
│   │   │   ├── skill.py
│   │   │   ├── prompt.md
│   │   │   └── tools.py
│   │   │
│   │   ├── rag_skill/
│   │   │   ├── skill.py
│   │   │   ├── prompt.md
│   │   │   └── tools.py
│   │   │
│   │   └── support_skill/
│   │       ├── skill.py
│   │       ├── prompt.md
│   │       └── tools.py
│   │
│   ├── tools/
│   │   ├── sql_tools.py
│   │   ├── rag_tools.py
│   │   └── shared_tools.py
│   │
│   ├── utils/
│   │   ├── embedding.py
│   │   ├── skill_matcher.py
│   │   └── logger.py
│   │
│   └── config.py
│
└── requirements.txt