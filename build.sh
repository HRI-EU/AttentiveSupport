# Set up the attentive support project with all dependencies
git submodule update --init --recursive
mkdir -p build && cd build && cmake ../src/Smile/ -DCMAKE_INSTALL_PREFIX=../install && make -j && make install
cd ..
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
source .venv/bin/activate
echo "All set."
