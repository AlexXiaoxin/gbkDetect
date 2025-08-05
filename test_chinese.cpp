#include <iostream>

// 正常中文注释
int main() {
    // 乱码测试：锟斤拷
    std::cout << "中文测试" << std::endl;
    std::cout << "乱码测试：��" << std::endl;
    return 0;
}