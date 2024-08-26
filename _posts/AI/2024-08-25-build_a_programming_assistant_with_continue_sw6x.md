---
layout: post
title: "使用Continue搭建编程助手"
date: 2024-08-25 22:38:59 +0800
categories: 技术
tags: AI Continue Ollama
---

Continue是开源AI代码助手。支持多种模型，比如ChatGPT，LLaMA等。我这里使用的是Ollama本地部署的模型当然也可以使用llama.cpp，Ollama部署起来更加的简单，所以这里以Ollama为例。

##  **Ollama配置**

编辑ollama服务，以便使其能对外提供服务且支持多模型并发访问。

```bash
sudo vim /etc/systemd/system/ollama.service
```

在 `[Service]` 下添加以下内容

```ini
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="OLLAMA_NUM_PARALLEL=4"
Environment="OLLAMA_MAX_LOADED_MODELS=4"
```

重新加载systemd并重新启动 Olama

```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```

拉取所需的模型

```bash
ollama pull llama3.1

ollama pull starcoder2:7b

ollama pull nomic-embed-text
```

## **Continue配置**

编辑 `continue` 的配置文件

```bash
vim ~/.continue/config.json
```

替换为以下内容，`models` 配置聊天模型，`tabAutocompleteModel` 配置代码tab补全模型。

```json
{
  "models": [
    {
      "title": "Llama3.1",
      "model": "llama3.1",
      "contextLength": 4096,
      "apiBase": "http://127.0.0.1:11434",
      "provider": "ollama"
    }
  ],
  "tabAutocompleteModel": {
    "title": "starcoder2",
    "provider": "ollama",
    "model": "starcoder2:7b",
    "apiBase": "http://127.0.0.1:11434"
  },
  "embeddingsProvider": {
    "title": "nomic-embed-text",
    "provider": "ollama",
    "model": "nomic-embed-text",
    "apiBase": "http://127.0.0.1:11434"
  }
}
```

## **使用效果**

![](/assets/images/post/截屏2024-08-26 10.21.03.png)

同时运行三个模型16G显存也有富裕，在 `ROCm` 的加速下，对话和代码补全的生成速度也是相当的快。

## **参考链接**

* <https://docs.continue.dev/intro>
* <https://ollama.com/>
* <https://beginor.github.io/2024/07/12/ai-code-assistant-with-local-llm.html>
* <https://blog.csdn.net/yao_zhuang/article/details/139552869>
