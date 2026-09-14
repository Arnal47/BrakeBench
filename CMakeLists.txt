cmake_minimum_required(VERSION 3.20)
project(BrakeBench LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

add_library(brake_ecu STATIC
    src/brake_controller.c
    src/diagnostics.c
    src/can_interface.c
    src/can_application_adapter.c
    src/brake_ecu.c)
target_include_directories(brake_ecu PUBLIC include)
target_compile_options(brake_ecu PRIVATE $<$<C_COMPILER_ID:MSVC>:/W4 /WX> $<$<NOT:$<C_COMPILER_ID:MSVC>>:-Wall -Wextra -Werror -pedantic>)

add_executable(brake_ecu_runner src/ecu_runner.c)
target_link_libraries(brake_ecu_runner PRIVATE brake_ecu)

enable_testing()
add_executable(ecu_unit_tests tests/c/test_brake_ecu.c)
target_link_libraries(ecu_unit_tests PRIVATE brake_ecu)
add_test(NAME ecu_unit_tests COMMAND ecu_unit_tests)
