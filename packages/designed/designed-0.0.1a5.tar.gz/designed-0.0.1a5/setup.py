from setuptools import setup, find_packages

setup(
    name="designed",
    version="0.0.1a5",
    packages=find_packages(),
    description="Module for Supporting the Creation of University Entrance Examination Mathematics Proofs Using a Symbolic Computation Module",
    long_description=open("README.md").read(),  # 長い説明（通常はREADME）
    long_description_content_type="text/markdown",  # 長い説明の形式
    author="chisakiShinichrouToshiyuki",
    author_email="designed.academy@gmail.com",
    url="https://github.com/chisakiShinichirouToshiyuki/designed",
    include_package_data=True,  # パッケージデータファイルを含める
    classifiers=[  # PyPIのメタデータ
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10.0, <3.12.0",
    install_requires=[  # 依存関係
        "sympy==1.11.*",
        "jedi>=0.16",
        "setuptools>65.5.1",
        "spb==0.1.*",
        "seaborn==0.12.*",
        "japanize_matplotlib>=1.1.0",
        "colorama==0.4.*",
    ],
    package_data={
        "": [
            "*.py", 
            "*.pyi", 
            "*.so",
            "*.pyd",
            "designed/jp/python_version_3_10/pyarmor_runtime_004089/linux_x86_64/pyarmor_runtime.so",
            "designed/jp/python_version_3_11/pyarmor_runtime_004089/linux_x86_64/pyarmor_runtime.so",
            "designed/jp/python_version_3_10/pyarmor_runtime_004089/darwin_x86_64/pyarmor_runtime.so",
            "designed/jp/python_version_3_11/pyarmor_runtime_004089/darwin_x86_64/pyarmor_runtime.so",
            "designed/jp/python_version_3_10/pyarmor_runtime_004089/windows_x86_64/pyarmor_runtime.pyd",
            "designed/jp/python_version_3_11/pyarmor_runtime_004089/windows_x86_64/pyarmor_runtime.pyd",
            "designed/en/python_version_3_10/pyarmor_runtime_004089/linux_x86_64/pyarmor_runtime.so",
            "designed/en/python_version_3_11/pyarmor_runtime_004089/linux_x86_64/pyarmor_runtime.so",
            "designed/en/python_version_3_10/pyarmor_runtime_004089/darwin_x86_64/pyarmor_runtime.so",
            "designed/en/python_version_3_11/pyarmor_runtime_004089/darwin_x86_64/pyarmor_runtime.so",
            "designed/en/python_version_3_10/pyarmor_runtime_004089/windows_x86_64/pyarmor_runtime.pyd",
            "designed/en/python_version_3_11/pyarmor_runtime_004089/windows_x86_64/pyarmor_runtime.pyd",
        ],
    },
)
