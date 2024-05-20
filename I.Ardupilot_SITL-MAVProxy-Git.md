### Ardupilot SITL Kurulumu

#### Git Kurulumu

Paket listelerini güncelleyelim.
```bash
sudo apt-get update
```

Yüklü paketleri en son sürüme yükseltelim.
```bash
sudo apt-get upgrade
```

```bash
sudo apt-get install git
```
-> Git'i yükler. Git, versiyon kontrol sistemidir.

```bash
sudo apt-get install gitk git-gui
```
-> Git'in grafiksel kullanıcı arayüzünü yükler (isteğe bağlı).

#### Ardupilot Dosyalarının İndirilmesi

```bash
git clone https://github.com/ArduPilot/ardupilot.git
```
-> Ardupilot'un GitHub deposunu klonlar.

```bash
cd ardupilot
```
-> İndirilen dizine geçer.

```bash
git submodule update --init --recursive
```
-> Ardupilot'un alt modüllerini başlatır ve günceller.

#### Gerekli Bileşenlerin Yüklenmesi

```bash
sudo apt install python-matplotlib python-serial python-wxgtk4.0 python-wxtools python-lxml python-scipy python-opencv ccache gawk python-pip python-pexpect
```
-> Ardupilot'un çalışması için gerekli olan Python paketlerini ve diğer bileşenleri yükler.

```bash
gedit ~/.bashrc
```
-> bashrc dosyasını düzenlemek için gedit'i açar.

```bash
export PATH=$PATH:$HOME/ardupilot/Tools/autotest
export PATH=/usr/lib/ccache:$PATH
```
-> PATH değişkenine ArduPilot ve ccache dizinlerini ekler.

```bash
. ~/.bashrc
```
-> bashrc dosyasındaki değişiklikleri uygular.

#### MAVProxy Kurulumu

```bash
sudo pip install future pymavlink MAVProxy
```
-> MAVProxy ve bağımlılıklarını yükler.

#### Ardupilot SITL Çalıştırılması

```bash
cd ~/ardupilot/ArduCopter
```
-> ArduCopter dizinine geçer.

```bash
../Tools/autotest/sim_vehicle.py -w --console --map
```
-> Ardupilot SITL'yi başlatır ve bir konsol ve harita penceresi açar.
