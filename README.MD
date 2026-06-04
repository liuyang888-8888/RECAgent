# RECAgent 代码仓库
Python==3.11.0
```shell
conda create -n RECAgent python=3.11.0
conda activate RECAgent
pip install -r requirements.txt
```
# RCAgent
1. 初始任务接收
2. 推断初始任务类型
3. 模态自适应需求提取

# WBAgent
1. 组件映射
2. 基础工作流构建
3. 参数更新


# 项目目录
RECAgent/  
├── Agent/          ------------- 多Agent核心算法逻辑  
│   ├── __init__.py   ------------ 工作流构建入口  
│   ├── RCAgent.py    ------------ 需求确认相关逻辑实现  
│   └── WBAgent.py    ------------ 工作流构建逻辑  
├── config/     -------------项目配置（数据库，AI Studio Accesstoken、画布, LLM，日志等）  
│   └── config.py  
├── data/          
│   ├── BenchMark/     ------------- 自然语言指令，分为 BI,RI,CI 三类指令  
│   └── csv/          -------------  复现对比对象使用的数据 csv 格式  
├── experiment/     -----------------研究内容一 实验结果（包括对比对象与消融实验）  
  ....  
│   └── NL2Workflow.py            -------------- 实验脚本  
├── lib/                     ----------- 一些简单的工具封装实现（如 find_project_root）  
├── llm/      -------------- 基于dashscope、openai等第三方平台大语言模型调用的统一封装接口  
├── logs/     
├── prompts/    ------------ 提示词  
├── test/      -------------- mysql、AI Studio、LLM等是否正常的测试脚本  
├── tools/     ------------- AI Studio 相关接口的封装工具类  
├── .gitignore  
├── README.md          ---------- 项目说明  
└── requirements.txt   ---------- 环境依赖  


