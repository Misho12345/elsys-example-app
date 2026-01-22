// use clang that supports C++23 for linux; for windows use the latest msvc compiler

import std;

class Sirene final
{
public:
    static Sirene& instance()
    {
        static Sirene s;
        return s;
    }

    void print_and_add1() { std::println("{}", value++); }

private:
    Sirene() = default;

    std::uint32_t value{};
};

int main()
{
    Sirene::instance().print_and_add1();
    Sirene::instance().print_and_add1();
    Sirene::instance().print_and_add1();
}
