# Industrijska robotika

Ovaj repozitorijum sadrzi kod sa vezbi iz predmeta Industrijska robotika.

Na predmetu se koristi:
- Ubuntu 24.04 LTS
- [ROS2 Jazzy](https://docs.ros.org/en/jazzy/index.html)


Za programiranje preporucuje se upotreba 
[VSCode IDE](https://code.visualstudio.com/download).

## Vezbe 1 - uvod u ROS

Uvodne vezbe pokrivaju:

- kreiranje ROS paketa
- ROS teme (topic)
- Publisher/Subscriber na temu
- tip poruke

### ROS workspace

Kreirati folder `ros_ws` i u njemu folder `src`. Ovo ce nam sluziti kao osnova,
i u `src` folderu cemo pisati kod za nas projekat.

U terminalu otidjite na lokaciju gde zelite da bude projekat i napravite folder 
projekta:
```sh
mkdir -p ros_ws/src
```

### Kreiranje paketa

Kako bismo izbegli manuelno kreiranje ROS 2 paketa, koristicemo gotovu komandu
koja ce automatski kreirati sve potrebne foldere i fajlove za nas. Svaki ROS 2
paket se sastoji od minimalno sledecih stvari:

- `package.xml` - meta podaci o nasem paketu (licenca, autor, opis, zavisnosti)
- `setup.cfg` - ako paket ima stvari za izvrsenje kako bi ih ROS pronasao
- `setup.py` - uputstva kako da se instalira paket
- `naziv_paketa/` - folder sa istim imenom kao i paket

Najpre je potrebno u terminalu preko `cd` komande otici u `ros_ws/src` folder,
a zatim u njemu pozvati komandu za kreiranje paketa:

```sh
ros2 pkg create --build-type ament_python --license Apache-2.0 <naziv_paketa>
```

Ovo ce kreirati ROS 2 paket sa minimalnom strukturom potrebnom za razvoj paketa
u Python programskom jeziku.

### Instaliranje paketa

Instaliranje (kompajliranje) paketa se postize izvrsavanjem komande `colcon build`
iz `ros_ws` foldera.

Nakon sto `colcon build` zavrsi instaliranje svih paketa, da bi oni bili vidljivi
u terminalu - da mozemo koristiti `ros2 run` komandu da pokrenemo kod iz nasih 
paketa, potrebno je pokrenuti komandu: `source install/setup.bash` iz `ros_ws` 
foldera. Ovu `source` komandu je potrebno izvrsiti u svakom novom terminalu.

**NAPOMENA**: nije potrebno pokretati `colcon build` u svakom novom terminalu,
nego samo nakon izmena u nasem kodu.  

### ROS Node

Nakon sto kreiramo paket `my_pkg` kreirati novi fajl `my_publisher.py` i u njemu
otkucati sledeci kod:

```py
import rclpy
from rclpy.node import Node

from std_msgs.msg import String


class MyNode(Node):

    def __init__(self):
        super().__init__('talker_node')
        self.publisher_ = self.create_publisher(String, 'talking', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.i = 0

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello World: %d' % self.i
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        self.i += 1


def main(args=None):
    rclpy.init(args=args)

    minimal_publisher = MinimalPublisher()

    rclpy.spin(minimal_publisher)

    minimal_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
```

Ovo je primer najprostijeg node-a koji periodicno objavljuje `String` podatak na temu
`talking`.

Za svaki fajl/cvor koji kreiramo, potrebno je da konfigurisemo: `package.xml` i
`setup.py`

Prvo, proveriti da li su: `<description>`, `<maintainer>` i `<license>` adekvatno
popunjeni.

Nakon toga, potrebno je dodati za nas primer sledece stvari:
```xml

<exec_depend>rclpy</exec_depend>
<exec_depend>std_msgs</exec_depend>
```

Ovo znaci da za vreme izvrsenja (`<exec_depend>`) nas cvor zavisi od `rclpy` i
`std_msgs` biblioteka.

Sledece, potrebno je podesiti `setup.py`, dodati:  
```py
entry_points={
        'console_scripts': [
                'talker = my_pkg.my_publisher:main',
        ],
},
```

Ovo znaci da cemo ukoliko zelimo da pokrenemo `main` funkciju iz naseg `my_publisher.py`
fajla, treba da pokrenemo komandu: `ros2 run my_pkg talker`. Dakle, sa leve strane
znaka jednako je alijas koji cemo koristiti u komandama, a sa desne strane je putanja
nase funkcije relativno u odnosu na `setup.py` kao `folder.naziv_fajla:naziv_funkcije`.


Identicnu stvar mozemo uraditi za cvor koji se prijavljuje na tu temu:

```py

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class MySub(Node):

    def __init__(self):
        # Naziv node-a 'listener'
        super().__init__("listener")
        # Kreiramo prijavu na temu `/talker`
        self.sub = self.create_subscription(String, "/talker", self.talker_cb, 10)

    def talker_cb(self, msg: String):
        # Ispisujemo sadrzaj poruke u terminalu
        self.get_logger().info(f"I've got: {msg.data}")


def main():
    rclpy.init()

    node = MySub()

    rclpy.spin(node)

    rclpy.shutdown()
```

Izmeniti `setup.py`:
```py
entry_points={
        'console_scripts': [
            'talker = my_pkg.my_publisher:main',
            'listener = my_pkg.my_subscriber:main'
        ],
    },
```


### Instaliranje dodatnih biblioteka

Ukoliko ROS paket zavisi od nekih biblioteka koje nisu instalirane na nasem
racunaru, potrebno je se osiguramo, pre `colcon build` komande, da su sve 
biblioteke dostupne. Ovo radimo pokretanjem komande iz `ros_ws` foldera:

```sh
rosdep install -i --from-path src --rosdistro jazzy -y
```
Nakon ovoga mozemo pokrenuti `colcon build`.


## Vezbe 2 - Launch, parametri, URDF

Cilj vezbi: kreirati Launch fajl koji ce istovremeno da pokrene dva cvora sa
prethodnih vezbi.

### kreiranje Launch fajla

U folderu naseg paketa, kreirati folder pod nazivom `launch` i u njemu Python
fajl sa sledecim sadrzajem:

```py

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='my_pkg',
            namespace='',
            executable='talker',
            name='talker',
            arguments=['--ros-args', '--log-level', 'info']  # koji nivo logovanja hocemo (obrisati --log-level i info ako hocemo sve)
        ),
        Node(
            package='my_pkg',
            namespace='',
            executable='listener',
            name='listener',
            ros_arguments=['--log-level', 'warn']
        ),
        
    ])
```

Za pakete koji imaju launch fajl, dobra je praksa dodati u `package.xml` da
paket zavisi od:
```xml
<exec_depend>ros2launch</exec_depend>
```
Svaki launch fajl bi trebalo da se zavrsava sa `<naziv_fajla>.launch.py` kako bi
ga ROS video nakon `source` komande.
Da bi `colcon build` instalirao launch fajl potrebno je dodati u `setup.py`
fajlu sledece: 

```py
import os
from glob import glob

package_name = 'my_pkg'

setup(
    # Other parameters ...
    data_files=[
        # ... Other data files
        # Include all launch files.
        (os.path.join('share', package_name, 'launch'), glob('launch/*'))
    ]
)
```


### parametri

ROS nam omogucava da svakom cvoru dodelimo neke parametre koje mozemo
konfigurisati i nakon kompajliranja paketa - na ovaj nacin se izbegava zalazenje
u source code i ponovno pokretanje komande `colcon build`.

YAML parametri mogu biti prosledjeni na dva nacina:
1. Putam argumenata u pokretanju cvora
2. Prosledjivanjem konfiguracionog fajla najcesce napisanog u [YAML](https://yaml.org/) formatu

__Prosledjivanje putem argumenata__

Preko terminala:
```sh
ros2 run package_name executable_name --ros-args -p param_name:=value
```

Preko launch fajla se parametri prosledjuju kao lista [recnika](https://docs.python.org/3/tutorial/datastructures.html#dictionaries).
Ne mora nuzno imati vise recnika, moze sve u jedan. Podrzava ugnjezdene parametre.
```py
Node(
    package="node_name",
    executable="executable_name",
    parameters=[
        {
            "param_name": param_value # int, str, float, bool, list
        }
    ]
)
```

__Prosledjivanje putem fajla__
```sh
ros2 run <package_name> <executable_name> --ros-args --params-file <file_name>
```

__Prosledjivanje putem fajla u launch-u__
```py

pkg_dir = get_package_share_directory("my_pkg")
yaml_path = pkg_dir + "/config/my_pkg.yaml"

Node(
    package="my_pkg",
    executable="talker",
    name="novi_talker",
    output="screen",

    parameters=[
        yaml_path
    ]

)
```

Da bi se YAML fajl instalirao, u `setup.py` je potrebno dodati:
```py
    # ...
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        # Launch
        (os.path.join("share", package_name, "launch"), glob(os.path.join("launch", "*.launch.py"))),

        # YAML - ovo smo dodali
        (os.path.join("share", package_name, "config"), glob(os.path.join("config", "*.yaml"))),
    # ...
```

### URDF

URDF predstavlja nacin modelovanja kinematske strukture robota. Napisan je u
[XML](https://developer.mozilla.org/en-US/docs/Web/XML/Guides/XML_introduction).

Opisuje vizuale, kolizije i inercije segmenta kao i zglobne veze izmedju segmenata.
Svaki zglob je definisan tipom i karakteristikama kao sto su:
- opseg pomeraja za pozicione (prismatic, revolute)
- maksimalna brzina
- osa oko koje, odnosno po kojoj, se zglob rotira/translira

Za nas primer URDF-a koristicemo xArm7 URDF iz paketa `xarm_description`. 
Verzija koju cemo koristiti se naziva `xarm7_with_gripper_camera.urdf`. 
Dobra praksa, odnosno konvencija, je da se stvari vezane za opis robota, kao sto
su URDF, nalaze u paketu sa sufiksom `_description`, dok je naziv paketa najcesce
naziv naseg robota.

URDF nam omogucava, nakon njegovog ucitavanja, da dobijemo homogene transformacije
izmedju bilo koja dva segmenta, ukljucujuci i transformaciju vrha robota u odnosu
na bazu robota. Za ovo je zasluzen [oficijalni paket](https://docs.ros.org/en/foxy/Tutorials/Intermediate/URDF/Using-URDF-with-Robot-State-Publisher.html) `robot_state_publisher` koji ocekuje najmanje jedan parametar: `robot_description`.
Vrednost ovog parametra je ucitan URDF fajl i objedinjen u jedan `string`. Kao
sto je dato u launch fajl primeru:

```py
xarm_pkg_dir = get_package_share_directory("xarm_description") # Putanja do instalacije paketa
xarm_urdf_path = xarm_pkg_dir + "/urdf/xarm7_with_gripper_camera.urdf" # putanja URDF fajla unutar paketa
xarm_urdf_str = open(xarm_urdf_path).read()

Node(
    package="robot_state_publisher",
    executable="robot_state_publisher",
    parameters=[
        {
            "robot_description": xarm_urdf_str
        }
    ]
)
```

Paket `robot_state_publisher` nam nakon ucitavanja URDF fajla daje transformacije
izmedju segmenata. Medjutim, posto se nas robot sastoji od zglobova koji mogu da
menjanju polozaj, `robot_state_publisher` se prijavljuje na temu `joint_states`
iz koje za svaki od zlogova cita vrednosti i azurira transformacije na osnovu toga.

Za simuliranje stanja zglobova i proveru ispravnosti URDF-a mozemo koristiti
[paket](https://docs.ros.org/en/jazzy/p/joint_state_publisher/) `joint_state_publisher`.
Ovom paketu se moze proslediti URDF ili ce se opciono prijaviti na temu `robot_description`
iz koje dobija informacije o kinematskoj strukturi robota i tipovima zglobova kao i njihovim parametrima.
Na linku se mogu videti parametri koje ovaj paket dodatno prihvata kao sto su:
- `rate` - brzina publikovanja na temu `joint_states`

U opstem slucaju, nas kontroler za robota je duzan da cita stanja zglobova (pozicija, brzina, itd)
i publikuje na `joint_states` temu. Paket `joint_state_publisher` se prilikom
upravljanja robotom ne koristi da ne bi uneo zabunu. Primer pokretanja ovog paketa:

```py
Node(
    package="joint_state_publisher_gui", # dodamo 'gui' na kraj 
    executable="joint_state_publisher_gui",
    parameters=[
        {
            "robot_description": xarm_urdf_str
        }
    ]
)
```

### RQT i RViz

RQT sluzi za vizualizaciju grafa ros mreze, izlistavanje tema, servisa i akcija,
kao i slanje podataka na iste. Takodje, moguce je vrsiti iscrtavanje grafika 
promene podataka sa teme (live plotting). 

Instalacija:
```sh
sudo apt install ros-jazzy-rqt*
```
Zvezdica znaci da ce pored `rqt` aplikacije biti instalirani i svi dodaci.

RViz je aplikacija za 3D vizualizaciju:
- robota
- putanja
- mape
- ostalih senzora

Koristi se pretezno za proveru i debuggovanje tokom razvoja. Pokretanje: 
```sh
ros2 run rviz2 rviz2
```