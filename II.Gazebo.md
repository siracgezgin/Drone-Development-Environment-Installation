### Gazebo Kurulumu

#### Gerekli İzinlerin Ayarlanması

```bash
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list'
```
-> Gazebo'nun kararlı sürümünün deposunu kaynak listesine ekler.

```bash
wget https://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -
```
-> Gazebo deposunun anahtarını indirir ve ekler.

#### Gazebo Kurulumu

```bash
sudo apt update
```
-> Paket listelerini günceller.

```bash
sudo apt-get install gazebo
```
-> Gazebo'yu yükler.

```bash
sudo apt-get install libgazebo-dev
```
-> Gazebo geliştirme kitaplıklarını yükler.

#### Gazebo Ardupilot Eklentisi Kurulumu

```bash
git clone https://github.com/khancyr/ardupilot_gazebo
```
-> ArduPilot Gazebo eklentisinin GitHub deposunu klonlar.

```bash
cd ardupilot_gazebo
```
-> ardupilot_gazebo dizinine geçer.

```bash
mkdir build
```
-> Derleme işlemleri için bir build dizini oluşturur.

```bash
cd build
```
-> build dizinine geçer.

```bash
cmake ..
```
-> CMake ile derleme dosyalarını oluşturur.

```bash
make -j4
```
-> Eklentiyi derler.

```bash
sudo make install
```
-> Eklentiyi yükler.

```bash
echo 'source /usr/share/gazebo/setup.sh' >> ~/.bashrc
```
-> Gazebo kurulumunu bashrc dosyasına ekler.

```bash
echo 'export GAZEBO_MODEL_PATH=~/ardupilot_gazebo/models' >> ~/.bashrc
```
-> Gazebo model yolunu bashrc dosyasına ekler.

```bash
. ~/.bashrc
```
-> bashrc dosyasındaki değişiklikleri uygular.

#### Gazebo Simülasyonu ve Ardupilot SITL'inin Başlatılması

```bash
gazebo --verbose worlds/iris_arducopter_runway.world
```
-> Gazebo'da bir dünya simülasyonu başlatır.

```bash
cd ~/ardupilot/ArduCopter
```
-> ArduCopter dizinine geçer.

```bash
../Tools/autotest/sim_vehicle.py -f gazebo-iris --console --map
```
-> ArduPilot SITL'yi Gazebo modunda başlatır ve bir konsol ve harita penceresi açar.
