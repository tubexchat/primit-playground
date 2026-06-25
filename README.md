# 📊 Primit Playground

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-green.svg)](https://python.org)

Primit Playground 是由 **Primit数据中心** 官方推出的开源量化投资与数据科学实战演练场。

本项目旨在为量化爱好者、数据科学家及金融从业者提供一条“从海量市场数据到自动化交易策略”的完整闭环路径。通过丰富的 Jupyter Notebook 教程与模块化代码，你将学会如何无缝对接 primit 高性能金融 API，并在此基础上进行指标计算、机器学习建模、因子挖掘与策略回测。

---

## 🔑 APIKEY 获取与配置 (API Key Configuration)

本项目中调用的美股、指数及大宗商品等 K 线数据接口需要按套餐等级进行鉴权，在使用前您需要先获取并配置 API 密钥（APIKEY）：

### 1. 获取方式
1. 访问 Primit 官方开发文档：[Primit Developer Docs](https://docs.pipai.org/)。
2. 注册并登录您的账户。
3. 进入控制台（Dashboard），在 [活动套餐 (Pricing)](https://docs.pipai.org/zh-Hans/pricing) 中根据需要订阅套餐（注：股票、指数、大宗商品的 K 线数据端点**至少需要订阅标准套餐**）。
4. 订阅成功后，平台会为您的账户签发一枚以 `pk_` 开头的**数据 API 密钥**。您可以在控制台中查看并管理它。

### 2. 配置方式
1. 在项目根目录下创建或编辑 `.env` 文件。
2. 将您获取到的数据 API 密钥填入 `.env` 文件中，指定为 `APIKEY` 变量，格式如下：
   ```env
   APIKEY=pk_xxxxxxxxxxxxxxxxxxxxxx
   ```
3. 代码运行中会自动通过请求头中的 `X-Primit-API-Key` 字段携带该密钥进行鉴权。详细说明可参考 [Primit 鉴权文档](https://docs.pipai.org/zh-Hans/auth)。

---

## 🎯 核心功能模块 (Core Modules)

### 1. 🌐 primit API 快速接入 (Data Acquisition)
* **全市场覆盖**：标准化的多品种金融市场历史与实时数据调用示例。
* **高并发优化**：包含流式数据接入、速率限制（Rate Limiting）处理及异常重试机制的最佳实践。

### 2. 📈 传统量化指标计算 (Quantitative Indicators)
* **趋势与动量**：基于高性能库（如 TA-Lib / Pandas）的高效指标计算逻辑。
* **经典复现**：内置 `MACD`（指数平滑异同移动平均线）、`RSI`（相对强弱指标）、`StochRSI`（随机相对强弱指标）等数十种量化因子工程底座。

### 3. 🧪 因子挖掘与工程 (Factor Mining & Alpha Generation)
* **因子构建**：从原始价量数据中清洗、交叉挖掘具有预测能力的 Alpha 因子。
* **有效性检验**：包含因子 IC/IR 测试、收益率分析及多空组合回测分析。

### 4. 🤖 机器学习与梯度提升模型 (Machine Learning & GBDT)
* **前沿模型集成**：利用 `XGBoost`、`LightGBM`、`CatBoost` 等主流梯度提升树模型进行价格趋势预测与分类。
* **时序特征工程**：专门针对金融时间序列（Time-Series）的交叉验证（Cross-Validation）与调参技巧，严防前瞻偏差（Look-ahead bias）。

### 5. 🔄 策略回测系统 (Strategy Backtesting)
* **高效回测**：基于主流回测框架（或精简版自定义引擎）进行策略验证。
* **多维评估**：自动输出夏普比率（Sharpe Ratio）、最大回撤（Max Drawdown）、胜率等专业级量化绩效评估报告。

---

## 🚀 为什么选择本项目？

* **生产级数据支撑**：所有示例均基于 primit 大数据中心真实、精准的金融全局数据流。
* **开箱即用 (Batteries Included)**：文档采用清晰的教程化结构，一行命令即可配置好本地研究环境。
* **完全开源与社区驱动**：遵循 MIT 开源协议，鼓励开发者提交 Issue 和 Pull Request，共同丰富生态。

