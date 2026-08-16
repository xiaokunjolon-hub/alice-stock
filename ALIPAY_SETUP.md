# 支付宝支付接入 — 状态与待办存档

更新时间：2026-08-16（已接通，收银台验证通过）

## 当前状态 ✅ 已接通可收款
- 支付宝「电脑网站支付」签约：**已生效**
- APPID、RSA2 密钥已换新，签名被支付宝接受，收银台页面正常打开
- 待办仅剩：**跑一单真实支付，确认异步回调把订单置为已付款**

## 关键参数（现行有效）
- **APPID** = `2021006190627209`（企业账号）
- **应用私钥** = 在 `/opt/alice-stock/.env` 的 `ALIPAY_PRIVATE_KEY`（单行 base64, PKCS#8 DER）
- **支付宝公钥** = 在 `/opt/alice-stock/.env` 的 `ALIPAY_PUBLIC_KEY`（单行 base64, SPKI DER）
- **网关** = `https://openapi.alipay.com/gateway.do`（正式环境）
- 签约产品：电脑网站支付（`product_code = FAST_INSTANT_TRADE_PAY`，method = `alipay.trade.page.pay`）
- `notify_url` = `https://stock.alicexie.com/api/public/alipay/notify`
- `return_url` = `https://www.alicexie.com/checkout.html?alipay=success&order_no={order_no}`

## 重要教训（别再踩坑）
- **个人支付宝账号开不了「电脑网站支付」**，必须企业/个体户账号。之前用个人账号的 APPID `2021006189652141` 一直报 `insufficient-isv-permissions`，就是这个原因。
- **「应用状态已上线」≠「产品已签约」**：前者在应用列表看，后者在「产品中心 → 电脑网站支付」看。
- **别把「签约申请编号」当成 APPID**：报 `invalid-app-id` 就是拿错了号。真 APPID 在应用详情页明确标注「APPID」字段。
- 排错看支付宝返回的错误码：`insufficient-isv-permissions`=产品未签约；`invalid-app-id`=APPID 填错；「验签失败」=密钥不对。

## 代码结构
- `/opt/alice-stock/app/routes/main.py`：
  - `POST /api/public/alipay/create-order` — 电脑网站支付下单，返回收银台跳转 URL
  - `POST /api/public/alipay/notify` — 异步回调，RSA2 验签，`TRADE_SUCCESS/TRADE_FINISHED` 时订单置 `paid`
  - `_alipay_sign` / `_alipay_verify` — RSA2 签名/验签（cryptography 库）
- 官网 `/opt/alice-website/out/checkout.html`：支付宝付款按钮 + `payWithAlipay()` + 支付成功回跳
- 配置在 `/opt/alice-stock/.env`（已 gitignore）；旧 `.env` 备份在 `.env.bak.*`

## 待办（最后一步）
1. **真实支付验证**：官网下一单 → 支付宝付款（可小额）→ 确认异步回调把订单置为 `paid`、`payment_method='alipay'`（库存系统 `/website-orders` 能看到状态流转）

## 备注
- 异步通知是 POST form，验签需剔除 `sign`/`sign_type` 后按 key 字母序拼 `key=value` 验签（已实现）
- 微信支付尚未接入（如需要可后续加）
- alice-stock 仓库是公开的且历史含旧 `.env`，旧密钥需轮换（另议）
