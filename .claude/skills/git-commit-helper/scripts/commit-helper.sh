#!/bin/bash
# Git 提交助手脚本 - 自动分析暂存更改并生成提交信息

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否有暂存的更改
check_staged_changes() {
    if ! git diff --staged --quiet; then
        return 0
    else
        return 1
    fi
}

# 显示暂存的更改
show_staged_changes() {
    print_info "当前暂存的更改："
    echo
    git status --short
    echo
    print_info "详细的更改内容："
    git diff --staged --stat
    echo
}

# 分析更改并建议提交类型
analyze_changes() {
    print_info "分析更改类型..."

    # 分析文件类型和更改模式
    local feat_files=$(git diff --staged --name-only | grep -E "\.(py|js|ts|jsx|tsx)$" || true)
    local test_files=$(git diff --staged --name-only | grep -E "test|spec" || true)
    local doc_files=$(git diff --staged --name-only | grep -E "\.(md|txt|rst|doc)$" || true)
    local config_files=$(git diff --staged --name-only | grep -E "\.(yml|yaml|json|toml|ini|cfg)$" || true)

    # 统计添加和删除的行数
    local added_lines=$(git diff --staged --numstat | awk '{sum += $1} END {print sum+0}')
    local deleted_lines=$(git diff --staged --numstat | awk '{sum += $2} END {print sum+0}')

    echo "更改统计："
    echo "  - 新增行数: $added_lines"
    echo "  - 删除行数: $deleted_lines"
    echo "  - 代码文件: $(echo "$feat_files" | wc -l | tr -d ' ')"
    echo "  - 测试文件: $(echo "$test_files" | wc -l | tr -d ' ')"
    echo "  - 文档文件: $(echo "$doc_files" | wc -l | tr -d ' ')"
    echo "  - 配置文件: $(echo "$config_files" | wc -l | tr -d ' ')"
    echo

    # 建议提交类型
    if [ -n "$test_files" ] && [ -z "$feat_files" ]; then
        echo "建议类型: test (主要是测试文件)"
    elif [ -n "$doc_files" ] && [ -z "$feat_files" ]; then
        echo "建议类型: docs (主要是文档更改)"
    elif [ -n "$config_files" ] && [ -z "$feat_files" ]; then
        echo "建议类型: chore (主要是配置更改)"
    elif [ "$added_lines" -gt "$deleted_lines" ]; then
        echo "建议类型: feat (新增代码较多)"
    elif [ "$deleted_lines" -gt "$((added_lines * 2))" ]; then
        echo "建议类型: refactor (大幅删除或重构)"
    else
        echo "建议类型: fix 或 refactor"
    fi
}

# 生成交互式提交信息
generate_commit_message() {
    echo
    print_info "请输入提交信息（遵循 Conventional Commits 格式）："
    echo "格式: <type>(<scope>): <description>"
    echo "类型: feat, fix, docs, style, refactor, test, chore"
    echo

    # 读取用户输入
    read -p "提交类型 (feat/fix/docs/refactor/test/chore): " type
    read -p "作用域 (可选，如 api/ui/db): " scope
    read -p "简短描述 (使用祈使语气): " description

    # 构建提交信息
    if [ -n "$scope" ]; then
        commit_msg="$type($scope): $description"
    else
        commit_msg="$type: $description"
    fi

    echo
    print_info "生成的提交信息："
    echo "$commit_msg"
    echo

    read -p "是否需要添加详细描述？(y/N): " add_detail
    if [[ $add_detail =~ ^[Yy]$ ]]; then
        echo "请输入详细描述（可选）："
        read -d '' detail
        commit_msg="$commit_msg\n\n$detail"
    fi

    echo
    print_info "完整提交信息："
    echo -e "$commit_msg"
    echo

    read -p "确认提交？(Y/n): " confirm
    if [[ ! $confirm =~ ^[Nn]$ ]]; then
        echo -e "$commit_msg" | git commit -F -
        print_success "提交成功！"
    else
        print_info "取消提交"
    fi
}

# 主函数
main() {
    print_info "Git 提交助手启动..."

    # 检查是否在 Git 仓库中
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "当前目录不是 Git 仓库"
        exit 1
    fi

    # 检查是否有暂存的更改
    if ! check_staged_changes; then
        print_warning "没有暂存的更改"
        echo
        print_info "可用操作："
        echo "1. 使用 'git add .' 暂存所有更改"
        echo "2. 使用 'git add -p' 交互式暂存"
        echo "3. 使用 'git add <file>' 暂存特定文件"
        echo
        read -p "是否自动暂存所有更改？(y/N): " auto_add
        if [[ $auto_add =~ ^[Yy]$ ]]; then
            git add .
            print_success "已暂存所有更改"
        else
            print_info "请先暂存更改后再运行此脚本"
            exit 0
        fi
    fi

    # 显示更改概览
    show_staged_changes

    # 分析更改
    analyze_changes

    # 生成交互式提交信息
    generate_commit_message
}

# 运行主函数
main "$@"