任务：

用 VS Code Dev Container 方式开发
代码与 GitHub 仓库 https://github.com/Ellyshome/AstrBot 同步
步骤
1. 
2. 创建 .devcontainer/devcontainer.json
基于项目现有的 Dockerfile，创建 Dev Container 配置：

使用 Dockerfile 构建开发镜像
挂载 data/ 目录到容器内（持久化用户数据）
映射端口 6185 (WebUI) 和 6199 (OneBot)
安装 VS Code 推荐扩展（Python、Pylance 等）
配置 git 凭证转发（利用 VS Code 自动处理）
关键文件：Dockerfile、compose.yml

4. 用 VS Code 打开 Dev Container
在 VS Code 中打开 ~/AstrBot/
VS Code 检测到 .devcontainer/ 后会提示 "Reopen in Container"
选择重新打开，VS Code 自动构建镜像并启动容器

5. 验证
git remote -v — 确认 origin 指向 Ellyshome/AstrBot，upstream 指向 Soulter/AstrBot
git status — 工作目录干净
访问 http://localhost:6185 — WebUI 正常
修改代码 → 宿主机文件同步更新 → git push 推送到 GitHub
需要创建的文件
.devcontainer/devcontainer.json — Dev Container 配置

验证方式
VS Code 成功在容器中打开项目
容器内 python main.py 可正常启动
宿主机和容器内代码双向同步
git push/pull 正常工作