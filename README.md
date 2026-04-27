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
        self.publisher_ = self.create_publisher(String, 'talker', 10)
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

    minimal_publisher = MyNode()

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
znaka jednako je alijas koji cemo koristiti u komandama, a sa desne strane je ono sto ce biti pozvano `naziv_paketa.naziv_modula:naziv_funkcije`. Paket je naziv foldera koji u sebi sadrzi `__init__.py` fajl, a modul je naziv python fajla iz tog paketa.


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
            ros_arguments=['--log-level', 'info']  # koji nivo logovanja hocemo (obrisati --log-level i info ako hocemo sve)
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
        (os.path.join('share', package_name, 'launch'), glob(os.path.join("launch", "*.launch.py")))
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
na bazu robota. Za ovo je zasluzen [oficijalni paket](https://docs.ros.org/en/jazzy/Tutorials/Intermediate/URDF/Using-URDF-with-Robot-State-Publisher.html) `robot_state_publisher` koji ocekuje najmanje jedan parametar: `robot_description`.
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

## Vezbe 3 - Moveit 2

MoveIt 2 je platforma za manipulaciju robotima kreirana za ROS 2. Sastoji se od naprednih algoritama za planiranje i sintezu trajektorije, kinematiku, upravljanje, itd.

Instalacija:
```sh
sudo apt install ros-jazzy-moveit*
```
Za integraciju naseg robota u MoveIt koristicemo njihov `setup_assistan.launch.py`.
Ovaj launch fajl pokrece GUI aplikaciju za konfiguraciju svega neophodnog kako bi
nasa robotska ruka mogla da se koristi sa Moveit-om.

Prvi korak je da buildujemo nase okruzenje (workspace):

```sh
colcon build --symlink-install
```

Zatim source:

```sh
source install/setup.bash
```

Pokretanje GUI aplikacije za MoveIt:

```sh
ros2 launch moveit_setup_assistant setup_assistant.launch.py 
```

Ukoliko imate integrisanu graficku karticu, pokrenuti sa sledecom komandom 
ukoliko dodje do greske prilikom ucitavanja URDF-a.

```sh
export QT_QPA_PLATFORM=xcb
ros2 launch moveit_setup_assistant setup_assistant.launch.py
```

Mozemo pratiti uputstvo sa [sajta](https://moveit.picknik.ai/main/doc/examples/setup_assistant/setup_assistant_tutorial.html)
na kome je objasnjeno detaljno sta koja stavka znaci i kako se konfigurise.

Ucitavamo fajl `xarm7_with_gripper_camera.urdf` is paketa `xarm_description`.

Nakon podesavanja svega, sacuvati u folder `xarm_moveit_config`.

Iz ovoga dobijamo `SRDF` fajl koji nam daje semanticki opis naseg robota.

### PREGLED STANJA

Instalirati sledece:
- `sudo apt install ros-jazzy-joint-state-publisher`
- `sudo apt install ros-jazzy-robot-state-publisher`
- `sudo apt install ros-jazzy-ros2-control*`
- `sudo apt install ros-jazzy-moveit*`
- `sudo apt install ros-jazzy-rqt*`

Paket `xarm_description` 
---
Sadrzi vizuale i kinematsku strukturu naseg robota.
Opisuje karakteristike zglobova i segmenata. Odavde ucitavamo URDF za
`MoveIt Setup Assistant` aplikaciju.

Paket `xarm_moveit_config` 
---
Nastaje kao rezultat konfigurisanja naseg robota
iz prethodno pomenute aplikacije. Sastoji se od `demo.launch.py` koji pokrece
nas sistem kako bismo ga testirali. Takodje sastoji se od sledecih konfiguracionih
fajlova:

- `initial_positions.yaml` - opisuje pocetna stanja zglobova naseg robota
- `joint_limits.yaml` - opisuje ogranicenja na brzinu i ubrzanja po zglobu
- `kinematics.yaml`- parametri algoritma za inverznu i direktnu kinematiku
- `ros2_controllers.yaml` - tipovi kontrolera i zglobovi vezani za svaki, u nasem slucaju ovi kontroleri su simulirani kao `FakeSystem` gde se svaka komanda izvrsava idealno. `ros2_control` paket ovo radi za nas. Na realnom robotu bi se koristila klasa iz `ros2_control` paketa koju bismo nasledili i implementirali odgovarajuce metode kako bismo ostvarili komunikaciju sa nasim robotom i spakovali poruke u odgovarajuci format. Ovde se ostvaruje npr. USB komunikacija ka robotu, ili TCP, ili nesto trece. Bilo koji vid fizicke komunikacije sa robotom je potrebno implementirati u _wrapper_  od `ros2_control` paketa
- `moveit_controllers.yaml` - parametri koji govore MoveIt-u na koje kontrolere da salje komande. Npr na *arm_controller* salje preko akcije `follow_joint_trajectory`. Neki opsti tok: 
    1. trazimo od Moveit da pomeri ruku u neki polozaj
    2. izvrsi se planiranje trajektorije (sekvenca pozicija zglobova kroz vreme)
    3. MoveIt pogleda parametre iz `moveit_controllers.yaml` da vidi koji kontroler je zaduzen za kretanje ruke i kako se zove akcija na koju salje
    4. MoveIt salje trajektoriju na `arm_controller/follow_joint_trajectory` server akcije
    5. `arm_controller` definisan u `ros2_controllers.yaml` koji je pokrenut u `ros2_control_node` poprima komandu i izvrsava je (prosledjuje stvarnom/laznom sistemu)

Paket `robot_move`
---
Pokrece sve potrebne alate kako bi upravljanje robotom bilo moguce:
- **robot_state_publisher**: publikuje transformacije izmedju zglobova na osnovu URDF i prijavljuje se na `joint_states` topic kako bi uvek imao azurno stanje o zglobovima

- **ros2_control_node**: iz paketa `controller_manager` pokrecemo ovaj node kome prosledjujemo odgovarajuce `ros2_controllers.yaml` parametre. Prijavljuje se na temu `robot_description` i ucitava `<ros2_control>` tagove iz URDF-a kako bi inicijalizovao potreban hardverski interfejs (u nasem slucaju `Fake`). Sluzi kao menadzer svih kontrolera. Zna za postojanje kontrolera: `arm_controller`, `hand_controller` i `joint_state_controller`, ali su neaktivni dok ne pozovemo `spawn`. Ono sto se u pozadini desava na svaku periodu upravljanje, npr 100 Hz, pozivaju se metode unutar `ros2_control_node`:
    1. prvo `read()` ka hardverskom interfejsu -> citamo trenutno stanje zglobova
    2. poziva se `update()` za svaki aktivan kontroler -> kontroler racuna sledecu komandu
    3. poziva se `write()` nad hardverskim interfejsom -> salje se komanda hardveru

- **joint_state_broadcaster**: citanjem iz URDF `<ros2_control>` tag-a, svi navedeni zglobovi se na svaku periodu citaju i salju na `joint_states` topic.

- **spawner**: poziva servise na `ros2_control_node` kako bi ucitao i aktivirao odredjeni kontroler. Prolazi kroz sledece korake:
    1. `/controller_manager/load_controller` - ucitava `.so` biblioteku kontrolera u memoriju procesa pomocu `pluginlib`-a, kontroler je u stanju `unconfigured`
    2. `/controller_manager/configure_controller` - kontroler cita svoje parametre i rezervise hardverske interfejse koje mu trebaju (npr. `joint1/position`). Ukoliko dva kontrolera pokusaju da rezervisu isti interfejs, konfiguracija ne uspeva. Kontroler prelazi u stanje `inactive`
    3. `/controller_manager/switch_controller` - kontroler postaje `active` i dodaje se u kontrolnu petlju. Od ovog trenutka se poziva njegova `update()` metoda (npr. na svakih 100Hz)

Nakon ovoga, interfejs ka robotu je spreman (bio on simuliran, fake ili pravi). Preostaje nam da ucitamo odgovarajuce parametre za __MoveIt__. 

MoveItPy node ocekuje sledece parametre kako bi mogao da vrsi planiranje i izvrsavanje:

```py
robot_move_node = Node(
    package='robot_move',
    executable='robot_move',
    output='screen',
    parameters=[
        {"robot_description": robot_description},           # URDF string (iz xacro)
        {"robot_description_semantic": srdf_content},       # SRDF string
        kinematics_yaml,        # parametri IK/FK solvera po grupama (arm, hand, itd)
        joint_limits_yaml,      # ogranicenja brzina i ubrzanja po zglobovima
        moveit_controllers_yaml,# adrese kontrolera ka kojima se salju trajektorije
        ompl_planning_yaml,     # konfiguracija OMPL planera (tip planera, parametri)
        moveit_cpp_yaml,        # opcije scene monitora, pipeline-ovi, podrazumevani parametri planiranja
    ]
)
```

**Ucitavanje parametara u launch fajlu**

```py
import os
from xacro import process_file
from ament_index_python.packages import get_package_share_directory

xarm_moveit_pkg_dir = get_package_share_directory('xarm_moveit_config')
robot_move_pkg_dir  = get_package_share_directory('robot_move')

# URDF - procitati i konvertovati iz xacro - voditi racuna ako radimo sa simuliranim/pravim robotom izmeniti ros2 tagove da plugin odgovara tome, u primeru se koristi mock_components/GenericSystem
robot_description = process_file(
    os.path.join(xarm_moveit_pkg_dir, 'config', 'UF_ROBOT.urdf.xacro')
).toxml()

# SRDF - procitati kao string
srdf_content = open(
    os.path.join(xarm_moveit_pkg_dir, 'config', 'UF_ROBOT.srdf')
).read()

robot_move_node = Node(
    package='robot_move',
    executable='robot_move',
    parameters=[
        {"robot_description": robot_description},
        {"robot_description_semantic": srdf_content},
        os.path.join(xarm_moveit_pkg_dir, 'config', 'kinematics.yaml'),
        os.path.join(xarm_moveit_pkg_dir, 'config', 'joint_limits.yaml'),
        os.path.join(xarm_moveit_pkg_dir, 'config', 'moveit_controllers.yaml'),
        os.path.join(xarm_moveit_pkg_dir, 'config', 'ompl_planning.yaml'),
        os.path.join(robot_move_pkg_dir,  'config', 'moveit_cpp.yaml'),
    ]
)
```

**Konfigurisanje planera - `moveit_cpp.yaml`**

U `moveit_cpp.yaml` se navodi koji su pipeline-ovi dostupni i koji se koristi podrazumevano:

```yaml
planning_pipelines:
  pipeline_names: ["ompl", "pilz_industrial_motion_planner"]

plan_request_params:
  planning_pipeline: ompl          # podrazumevani planer
  planning_time: 5.0
  max_velocity_scaling_factor: 1.0
  max_acceleration_scaling_factor: 1.0
```

**Promena planera u Python kodu**

```py
from moveit.planning import MoveItPy, PlanRequestParameters

robot = MoveItPy(node_name="robot_move_moveit")
arm   = robot.get_planning_component("arm")

arm.set_start_state_to_current_state()
arm.set_goal_state(configuration_name="home")

# --- OMPL ---
ompl_params = PlanRequestParameters(robot, "ompl")
ompl_params.planner_id = "RRTConnectkConfigDefault"
ompl_params.planning_time = 5.0

# --- Pilz PTP (point-to-point, zglobni prostor) ---
pilz_ptp = PlanRequestParameters(robot, "pilz_industrial_motion_planner")
pilz_ptp.planner_id = "PTP"
pilz_ptp.max_velocity_scaling_factor = 0.5

# --- Pilz LIN (linearna putanja u kartezijanskom prostoru) ---
pilz_lin = PlanRequestParameters(robot, "pilz_industrial_motion_planner")
pilz_lin.planner_id = "LIN"

# Odabir planera se vrsi prosledjivanjem parametara u plan()
plan = arm.plan(plan_request_parameters=ompl_params)
# ili
plan = arm.plan(plan_request_parameters=pilz_ptp)

if plan:
    robot.execute(plan.trajectory, controllers=[])
```

Dostupni `planner_id` vrednosti za pipeline:

- **`ompl`**:   
    - SBL
    - EST
    - LBKPIECE
    - BKPIECE
    - KPIECE
    - RRT
    - RRTConnect
    - RRTstar
    - TRRT
    - PRM
    - PRMstar
    - FMT
    - BFMT
    - PDST
    - STRIDE
    - BiTRRT
    - LBTRRT
    - BiEST
    - ProjEST
    - LazyPRM
    - LazyPRMstar
    - SPARS
    - SPARStwo

- **`pilz_industrial_motion_planner	`**:
    - PTP
    - LIN : linearno kretanje, koriste se `cartesian limits` parametri za generisanje profila brzine
    - CIRC : cirkularno (kruzno) kretanje

---

Posto MoveItPy ocekuje da su parametri planera u _namespace_-u pod odgovarajucim imenom, ucitane YAML fajlove je potrebno proslediti kao parametri u node gde se pokrece MoveItPy kao:

```py
import yaml

def load_yaml(file_path):
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

robot_move_pkg_dir = get_package_share_directory('robot_move')

ompl_config = load_yaml(
    os.path.join(robot_move_pkg_dir, 'config', 'ompl_planning.yaml')
)
pilz_config = load_yaml(
    os.path.join(robot_move_pkg_dir, 'config', 'pilz_industrial_motion_planner_planning.yaml')
)

robot_move_node = Node(
    package='robot_move',
    executable='robot_move',
    parameters=[
        {"robot_description": robot_description},
        {"robot_description_semantic": srdf_content},
        os.path.join(xarm_moveit_pkg_dir, 'config', 'kinematics.yaml'),
        os.path.join(xarm_moveit_pkg_dir, 'config', 'joint_limits.yaml'),
        os.path.join(xarm_moveit_pkg_dir, 'config', 'moveit_controllers.yaml'),
        {"ompl": ompl_config},                                          # namespace mora da odgovara imenu pipeline-a
        {"pilz_industrial_motion_planner": pilz_config},                # isti princip
        os.path.join(robot_move_pkg_dir, 'config', 'moveit_cpp.yaml'), # pipeline_names mora sadrzati oba
    ]
)
```