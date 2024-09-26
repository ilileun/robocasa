from robocasa.environments.kitchen.kitchen import *

from loguru import logger

# 로거 설정
logger.add("debug.log", rotation="500 MB")


class PnP(Kitchen):
    """
    Class encapsulating the atomic pick and place tasks.

    Args:
        obj_groups (str): Object groups to sample the target object from.

        exclude_obj_groups (str): Object groups to exclude from sampling the target object.
    """

    def __init__(self, obj_groups="all", exclude_obj_groups=None, *args, **kwargs):
        logger.info(
            f"Initializing PnP with obj_groups={obj_groups}, exclude_obj_groups={exclude_obj_groups}"
        )
        self.obj_groups = obj_groups
        self.exclude_obj_groups = exclude_obj_groups

        super().__init__(*args, **kwargs)

    def _get_obj_cfgs(self):
        raise NotImplementedError


class PnPCounterToCab(PnP):
    """
    Class encapsulating the atomic counter to cabinet pick and place task

    Args:
        cab_id (str): The cabinet fixture id to place the object.

        obj_groups (str): Object groups to sample the target object from.
    """

    def __init__(
        self, cab_id=FixtureType.CABINET_TOP, obj_groups="all", *args, **kwargs
    ):
        logger.info(
            f"Initializing PnPCounterToCab with cab_id={cab_id}, obj_groups={obj_groups}"
        )
        self.cab_id = cab_id
        super().__init__(obj_groups=obj_groups, *args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the counter to cabinet pick and place task:
        The cabinet to place object in and the counter to initialize it on
        """
        super()._setup_kitchen_references()
        try:
            self.island = self.register_fixture_ref(
                "island",
                dict(id=FixtureType.ISLAND),
            )
        except AssertionError:
            print(
                "Warning: Island not found in the current layout. Using an alternative fixture."
            )
            # 대체 fixture 사용 (예: 첫 번째 사용 가능한 counter)
            self.island = self.register_fixture_ref(
                "island",
                dict(id=FixtureType.COUNTER),  # island 대신 counter로 대체!!
            )

        self.cab = self.register_fixture_ref("cab", dict(id=self.cab_id))
        # self.counter = self.register_fixture_ref(
        #     "counter", dict(id=FixtureType.COUNTER, ref=self.cab)
        # )

        # self.init_robot_base_pos = self.cab

        # ==============

        self.microwave = self.register_fixture_ref(
            "microwave",
            dict(id=FixtureType.MICROWAVE),
        )
        self.counter = self.register_fixture_ref(
            "counter",
            dict(id=FixtureType.COUNTER, ref=self.microwave),
        )
        self.distr_counter = self.register_fixture_ref(
            "distr_counter",
            dict(id=FixtureType.COUNTER, ref=self.microwave),
        )
        self.fridge = self.register_fixture_ref(
            "fridge",
            dict(id=FixtureType.FRIDGE),
        )

        self.init_robot_base_pos = self.island

        logger.debug(
            f"Kitchen references set up: cab={self.cab}, counter={self.counter}"
        )

    def get_ep_meta(self):
        """
        Get the episode metadata for the counter to cabinet pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        obj_lang = self.get_obj_lang()
        ep_meta[
            "lang"
        ] = f"pick the {obj_lang} from the counter and place it in the cabinet"

        logger.info(f"obj_lang: {obj_lang}")
        logger.info(f'episode for em_meta["lang"]: {ep_meta["lang"]}')
        # logger.info(f"Episode metadata: {ep_meta}")
        return ep_meta

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()
        # self.cab.set_door_state(min=0.90, max=1.0, env=self, rng=self.rng)

        ##############################

        # self.microwave.set_door_state(min=0.90, max=1.0, env=self, rng=self.rng)

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the counter to cabinet pick and place task.
        Puts the target object in the front area of the counter. Puts a distractor object on the counter
        and the back area of the cabinet.

        """
        cfgs = []
        cfgs.append(
            dict(
                name="obj",
                obj_groups=self.obj_groups,
                exclude_obj_groups=self.exclude_obj_groups,
                graspable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(0.60, 0.30),
                    pos=(0.0, -1.0),
                    offset=(0.0, 0.10),
                ),
            )
        )

        # distractors
        cfgs.append(
            dict(
                name="distr_counter",
                obj_groups="all",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(1.0, 0.30),
                    pos=(0.0, 1.0),
                    offset=(0.0, -0.05),
                ),
            )
        )
        cfgs.append(
            dict(
                name="distr_cab",
                obj_groups="all",
                placement=dict(
                    fixture=self.cab,
                    size=(1.0, 0.20),
                    pos=(0.0, 1.0),
                    offset=(0.0, 0.0),
                ),
            )
        )

        # cfgs.append(
        #     dict(
        #         name="tomato",  # 여기 이름은 자유롭게 가능
        #         obj_groups="tomato",  # 오브젝트 이름 !
        #         # placement=dict(
        #         #     fixture=self.counter,
        #         #     sample_region_kwargs=dict(
        #         #         ref=self.cab,
        #         #     ),
        #         #     size=(0.35, 0.2),
        #         #     pos=("ref", -1.0),
        #         # ),
        #         placement=dict(
        #             fixture=self.island,
        #             size=(0.0, 0.0),  # 이동할 수 있는 범위 설정
        #             pos=(0.0, 0.0),
        #             offset=(0.0, 0.0),
        #         ),
        #         ensure_object_boundary_in_range=True,
        #     )
        # )

        """
        Get the object configurations for the counter to cabinet pick and place task.
        Spawns 30 objects randomly on the island.
        """
        # Island의 크기를 가져옵니다. 이 부분은 실제 환경에 맞게 조정해야 할 수 있습니다.
        island_size = self.island.size
        spawn_object_num = 30

        # 30개의 object를 생성합니다.
        for i in range(spawn_object_num):
            cfgs.append(
                dict(
                    name=f"object_{i}",  # 각 객체에 고유한 이름을 부여합니다.
                    obj_groups="all",  # 모든 객체 그룹에서 선택합니다. 필요에 따라 변경 가능합니다.
                    # graspable=True,
                    # cookable=True,
                    placement=dict(
                        fixture=self.island,
                        size=(
                            island_size[0] * 0.6,
                            island_size[1] * 0.6,
                        ),  # island 크기의 80%를 사용 영역으로 설정
                        pos=(0.0, 0.0),  # island의 중심을 기준으로 합니다.
                        offset=(0.0, 0.0),
                    ),
                    ensure_object_boundary_in_range=True,
                )
            )

        # spawn 되는 물체의 상세 정보..
        # logger.info(f"Distractor in cabinet configuration: {cfgs}")
        # spawn 되는 물체의 개수..
        logger.info(f"Total number of object configurations: {len(cfgs)}")

        return cfgs

    def _check_success(self):
        """
        Check if the counter to cabinet pick and place task is successful.
        Checks if the object is inside the cabinet and the gripper is far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        obj_inside_cab = OU.obj_inside_of(self, "obj", self.cab)
        gripper_obj_far = OU.gripper_obj_far(self)

        ## check if the object is inside the cabinet!
        success = obj_inside_cab and gripper_obj_far
        # logger.info(f"Task success check: obj_inside_cab={obj_inside_cab}, gripper_obj_far={gripper_obj_far}, success={success}")
        if success:
            logger.info(
                f"Task success check: obj_inside_cab={obj_inside_cab}, gripper_obj_far={gripper_obj_far}, success={success}"
            )

        return obj_inside_cab and gripper_obj_far


class PnPCabToCounter(PnP):
    """
    Class encapsulating the atomic cabinet to counter pick and place task

    Args:
        cab_id (str): The cabinet fixture id to pick the object from.

        obj_groups (str): Object groups to sample the target object from.
    """

    def __init__(
        self, cab_id=FixtureType.CABINET_TOP, obj_groups="all", *args, **kwargs
    ):
        self.cab_id = cab_id
        super().__init__(obj_groups=obj_groups, *args, **kwargs)
        logger.info(
            f"Initializing PnPCabToCounter with cab_id={cab_id}, obj_groups={obj_groups}"
        )

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the cabinet to counter pick and place task:
        The cabinet to pick object from and the counter to place it on
        """
        super()._setup_kitchen_references()
        self.cab = self.register_fixture_ref(
            "cab",
            dict(id=self.cab_id),
        )
        self.counter = self.register_fixture_ref(
            "counter",
            dict(id=FixtureType.COUNTER, ref=self.cab),
        )
        self.init_robot_base_pos = self.cab

    def get_ep_meta(self):
        """
        Get the episode metadata for the cabinet to counter pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        obj_lang = self.get_obj_lang()
        ep_meta[
            "lang"
        ] = f"pick the {obj_lang} from the cabinet and place it on the counter"
        return ep_meta

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()
        # 여기가 서랍장 여는 부분으로..
        self.cab.set_door_state(min=0.90, max=1.0, env=self, rng=self.rng)

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the cabinet to counter pick and place task.
        Puts the target object in the front area of the cabinet. Puts a distractor object on the counter
        and the back area of the cabinet.
        """
        cfgs = []
        cfgs.append(
            dict(
                name="obj",
                obj_groups=self.obj_groups,
                exclude_obj_groups=self.exclude_obj_groups,
                graspable=True,
                placement=dict(
                    fixture=self.cab,
                    size=(0.50, 0.20),
                    pos=(0, -1.0),
                ),
            )
        )

        # distractors
        cfgs.append(
            dict(
                name="distr_counter",
                obj_groups="all",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.cab,
                    ),
                    size=(1.0, 0.30),
                    pos=(0.0, 1.0),
                    offset=(0.0, -0.05),
                ),
            )
        )
        cfgs.append(
            dict(
                name="distr_cab",
                obj_groups="all",
                placement=dict(
                    fixture=self.cab,
                    size=(1.0, 0.20),
                    pos=(0.0, 1.0),
                    offset=(0.0, 0.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the cabinet to counter pick and place task is successful.
        Checks if the object is on the counter and the gripper is far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        gripper_obj_far = OU.gripper_obj_far(self)
        obj_on_counter = OU.check_obj_fixture_contact(self, "obj", self.counter)
        return obj_on_counter and gripper_obj_far


class PnPCounterToSink(PnP):
    """
    Class encapsulating the atomic counter to sink pick and place task

    Args:
        obj_groups (str): Object groups to sample the target object from.
    """

    def __init__(self, obj_groups="all", *args, **kwargs):

        super().__init__(obj_groups=obj_groups, *args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the counter to sink pick and place task:
        The sink to place object in and the counter to initialize it on
        """
        super()._setup_kitchen_references()
        self.sink = self.register_fixture_ref(
            "sink",
            dict(id=FixtureType.SINK),
        )
        self.counter = self.register_fixture_ref(
            "counter",
            dict(id=FixtureType.COUNTER, ref=self.sink),
        )
        self.init_robot_base_pos = self.sink

    def get_ep_meta(self):
        """
        Get the episode metadata for the counter to sink pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        obj_lang = self.get_obj_lang()
        ep_meta[
            "lang"
        ] = f"pick the {obj_lang} from the counter and place it in the sink"
        return ep_meta

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the counter to sink pick and place task.
        Puts the target object in the front area of the counter. Puts a distractor object on the counter
        and the sink.
        """
        cfgs = []
        cfgs.append(
            dict(
                name="obj",
                obj_groups=self.obj_groups,
                exclude_obj_groups=self.exclude_obj_groups,
                graspable=True,
                washable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.30, 0.40),
                    pos=("ref", -1.0),
                ),
            )
        )

        # distractors
        cfgs.append(
            dict(
                name="distr_counter",
                obj_groups="all",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", -1.0),
                    offset=(0.0, 0.30),
                ),
            )
        )
        cfgs.append(
            dict(
                name="distr_sink",
                obj_groups="all",
                washable=True,
                placement=dict(
                    fixture=self.sink,
                    size=(0.25, 0.25),
                    pos=(0.0, 1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the counter to sink pick and place task is successful.
        Checks if the object is inside the sink and the gripper is far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        obj_in_sink = OU.obj_inside_of(self, "obj", self.sink)
        gripper_obj_far = OU.gripper_obj_far(self)
        return obj_in_sink and gripper_obj_far


class PnPSinkToCounter(PnP):
    """
    Class encapsulating the atomic sink to counter pick and place task

    Args:
        obj_groups (str): Object groups to sample the target object from.
    """

    def __init__(self, obj_groups="food", *args, **kwargs):

        super().__init__(obj_groups=obj_groups, *args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the sink to counter pick and place task:
        The sink to pick object from and the counter to place it on
        """
        super()._setup_kitchen_references()
        self.sink = self.register_fixture_ref(
            "sink",
            dict(id=FixtureType.SINK),
        )
        self.counter = self.register_fixture_ref(
            "counter",
            dict(id=FixtureType.COUNTER, ref=self.sink),
        )
        self.init_robot_base_pos = self.sink

    def get_ep_meta(self):
        """
        Get the episode metadata for the sink to counter pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        obj_lang = self.get_obj_lang()
        cont_lang = self.get_obj_lang(obj_name="container")
        ep_meta[
            "lang"
        ] = f"pick the {obj_lang} from the sink and place it on the {cont_lang} located on the counter"
        return ep_meta

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the sink to counter pick and place task.
        Puts the target object in the sink. Puts a distractor object on the counter
        and places a container on the counter for the target object to be placed on.
        """
        cfgs = []
        cfgs.append(
            dict(
                name="obj",
                obj_groups=self.obj_groups,
                exclude_obj_groups=self.exclude_obj_groups,
                graspable=True,
                washable=True,
                placement=dict(
                    fixture=self.sink,
                    size=(0.25, 0.25),
                    pos=(0.0, 1.0),
                ),
            )
        )
        cfgs.append(
            dict(
                name="container",
                obj_groups="container",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.35, 0.40),
                    pos=("ref", -1.0),
                ),
            )
        )

        # distractors
        cfgs.append(
            dict(
                name="distr_counter",
                obj_groups="all",
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.sink,
                        loc="left_right",
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", -1.0),
                    offset=(0.0, 0.30),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the sink to counter pick and place task is successful.
        Checks if the object is in the container, the container on the counter, and the gripper far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        obj_in_recep = OU.check_obj_in_receptacle(self, "obj", "container")
        recep_on_counter = self.check_contact(self.objects["container"], self.counter)
        gripper_obj_far = OU.gripper_obj_far(self)
        return obj_in_recep and recep_on_counter and gripper_obj_far


class PnPCounterToMicrowave(PnP):
    # exclude layout 8 because the microwave is far from counters
    EXCLUDE_LAYOUTS = [8]
    """
    Class encapsulating the atomic counter to microwave pick and place task

    Args:
        obj_groups (str): Object groups to sample the target object from.
    """

    def __init__(self, obj_groups="food", *args, **kwargs):
        super().__init__(obj_groups=obj_groups, *args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the counter to microwave pick and place task:
        The microwave to place object on, the counter to initialize it/the container on, and a distractor counter
        """
        super()._setup_kitchen_references()
        self.microwave = self.register_fixture_ref(
            "microwave",
            dict(id=FixtureType.MICROWAVE),
        )
        self.counter = self.register_fixture_ref(
            "counter",
            dict(id=FixtureType.COUNTER, ref=self.microwave),
        )
        self.distr_counter = self.register_fixture_ref(
            "distr_counter",
            dict(id=FixtureType.COUNTER, ref=self.microwave),
        )
        self.init_robot_base_pos = self.microwave

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()
        self.microwave.set_door_state(min=0.90, max=1.0, env=self, rng=self.rng)

    def get_ep_meta(self):
        """
        Get the episode metadata for the counter to microwave pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        obj_lang = self.get_obj_lang()
        ep_meta[
            "lang"
        ] = f"pick the {obj_lang} from the counter and place it in the microwave"
        return ep_meta

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the counter to microwave pick and place task.
        Puts the target object in a container on the counter. Puts a distractor object on the distractor
        counter and places another container in the microwave.
        """
        cfgs = []

        cfgs.append(
            dict(
                name="obj",
                obj_groups=self.obj_groups,
                exclude_obj_groups=self.exclude_obj_groups,
                graspable=True,
                microwavable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.microwave,
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", -1.0),
                    try_to_place_in="container",
                ),
            )
        )
        cfgs.append(
            dict(
                name="container",
                obj_groups=("plate"),
                placement=dict(
                    fixture=self.microwave,
                    size=(0.05, 0.05),
                    ensure_object_boundary_in_range=False,
                ),
            )
        )

        # distractors
        cfgs.append(
            dict(
                name="distr_counter",
                obj_groups="all",
                placement=dict(
                    fixture=self.distr_counter,
                    sample_region_kwargs=dict(
                        ref=self.microwave,
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", 1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the counter to microwave pick and place task is successful.
        Checks if the object is inside the microwave and on the container and the gripper is far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        obj = self.objects["obj"]
        container = self.objects["container"]

        obj_container_contact = self.check_contact(obj, container)
        container_micro_contact = self.check_contact(container, self.microwave)
        gripper_obj_far = OU.gripper_obj_far(self)
        return obj_container_contact and container_micro_contact and gripper_obj_far


class PnPMicrowaveToCounter(PnP):
    # exclude layout 8 because the microwave is far from counters
    EXCLUDE_LAYOUTS = [8]
    """
    Class encapsulating the atomic microwave to counter pick and place task

    Args:
        obj_groups (str): Object groups to sample the target object from.
    """

    def __init__(self, obj_groups="food", *args, **kwargs):

        super().__init__(obj_groups=obj_groups, *args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the microwave to counter pick and place task:
        The microwave to pick object from, the counter to place it on, and a distractor counter
        """
        super()._setup_kitchen_references()
        self.microwave = self.register_fixture_ref(
            "microwave",
            dict(id=FixtureType.MICROWAVE),
        )
        self.counter = self.register_fixture_ref(
            "counter",
            dict(id=FixtureType.COUNTER, ref=self.microwave),
        )
        self.distr_counter = self.register_fixture_ref(
            "distr_counter",
            dict(id=FixtureType.COUNTER, ref=self.microwave),
        )
        self.init_robot_base_pos = self.microwave

    def _reset_internal(self):
        """
        Resets simulation internal configurations.
        """
        super()._reset_internal()
        self.microwave.set_door_state(min=0.90, max=1.0, env=self, rng=self.rng)

    def get_ep_meta(self):
        """
        Get the episode metadata for the microwave to counter pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        obj_lang = self.get_obj_lang()
        cont_lang = self.get_obj_lang(obj_name="container")
        ep_meta[
            "lang"
        ] = f"pick the {obj_lang} from the microwave and place it on {cont_lang} located on the counter"
        return ep_meta

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the microwave to counter pick and place task.
        Puts the target object in a container in the microwave. Puts a distractor object on the distractor
        counter and places another container on the counter."""
        cfgs = []

        cfgs.append(
            dict(
                name="obj",
                obj_groups=self.obj_groups,
                exclude_obj_groups=self.exclude_obj_groups,
                graspable=True,
                microwavable=True,
                placement=dict(
                    fixture=self.microwave,
                    size=(0.05, 0.05),
                    ensure_object_boundary_in_range=False,
                    try_to_place_in="container",
                ),
            )
        )
        cfgs.append(
            dict(
                name="container",
                obj_groups=("container"),
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.microwave,
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", -1.0),
                ),
            )
        )

        # distractors
        cfgs.append(
            dict(
                name="distr_counter",
                obj_groups="all",
                placement=dict(
                    fixture=self.distr_counter,
                    sample_region_kwargs=dict(
                        ref=self.microwave,
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", 1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the microwave to counter pick and place task is successful.
        Checks if the object is inside the container and the gripper far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        obj_container_contact = OU.check_obj_in_receptacle(self, "obj", "container")
        gripper_obj_far = OU.gripper_obj_far(self)
        return obj_container_contact and gripper_obj_far


class PnPCounterToStove(PnP):
    """
    Class encapsulating the atomic counter to stove pick and place task

    Args:
        obj_groups (str): Object groups to sample the target object from.
    """

    def __init__(self, obj_groups="food", *args, **kwargs):
        super().__init__(obj_groups=obj_groups, *args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the counter to stove pick and place task:
        The stove to place object on and the counter to initialize it/container on
        """
        super()._setup_kitchen_references()
        self.stove = self.register_fixture_ref("stove", dict(id=FixtureType.STOVE))
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.stove, size=[0.30, 0.40])
        )
        self.init_robot_base_pos = self.stove

    def get_ep_meta(self):
        """
        Get the episode metadata for the counter to stove pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        obj_lang = self.get_obj_lang()
        cont_lang = self.get_obj_lang(obj_name="container")
        ep_meta[
            "lang"
        ] = f"pick the {obj_lang} from the plate and place it in the {cont_lang}"
        return ep_meta

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the counter to stove pick and place task.
        Puts the target object in a container on the counter and places pan on the stove.
        """
        cfgs = []

        cfgs.append(
            dict(
                name="container",
                obj_groups=("pan"),
                placement=dict(
                    fixture=self.stove,
                    ensure_object_boundary_in_range=False,
                    size=(0.02, 0.02),
                    rotation=[(-3 * np.pi / 8, -np.pi / 4), (np.pi / 4, 3 * np.pi / 8)],
                ),
            )
        )

        cfgs.append(
            dict(
                name="obj",
                obj_groups=self.obj_groups,
                exclude_obj_groups=self.exclude_obj_groups,
                graspable=True,
                cookable=True,
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.stove,
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", -1.0),
                    try_to_place_in="container",
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the counter to stove pick and place task is successful.
        Checks if the object is on the pan and the gripper far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        obj_in_container = OU.check_obj_in_receptacle(self, "obj", "container", th=0.07)
        gripper_obj_far = OU.gripper_obj_far(self)

        return obj_in_container and gripper_obj_far


class PnPStoveToCounter(PnP):
    """
    Class encapsulating the atomic stove to counter pick and place task
    """

    def __init__(self, obj_groups="food", *args, **kwargs):
        super().__init__(obj_groups=obj_groups, *args, **kwargs)

    def _setup_kitchen_references(self):
        """
        Setup the kitchen references for the stove to counter pick and place task:
        The counter to place object/container on and the stove to initialize it/the pan on
        """
        super()._setup_kitchen_references()
        self.stove = self.register_fixture_ref("stove", dict(id=FixtureType.STOVE))
        self.counter = self.register_fixture_ref(
            "counter", dict(id=FixtureType.COUNTER, ref=self.stove, size=[0.30, 0.40])
        )
        self.init_robot_base_pos = self.stove

    def get_ep_meta(self):
        """
        Get the episode metadata for the stove to counter pick and place task.
        This includes the language description of the task.
        """
        ep_meta = super().get_ep_meta()
        obj_lang = self.get_obj_lang()
        obj_cont_lang = self.get_obj_lang(obj_name="obj_container")
        cont_lang, preposition = self.get_obj_lang(
            obj_name="container", get_preposition=True
        )
        ep_meta[
            "lang"
        ] = f"pick the {obj_lang} from the {obj_cont_lang} and place it {preposition} the {cont_lang}"
        return ep_meta

    def _get_obj_cfgs(self):
        """
        Get the object configurations for the stove to counter pick and place task.
        Puts the target object in a pan on the stove and places a container on the counter.
        """
        cfgs = []

        cfgs.append(
            dict(
                name="obj",
                obj_groups=self.obj_groups,
                exclude_obj_groups=self.exclude_obj_groups,
                graspable=True,
                cookable=True,
                max_size=(0.15, 0.15, None),
                placement=dict(
                    fixture=self.stove,
                    ensure_object_boundary_in_range=False,
                    size=(0.02, 0.02),
                    rotation=[(-3 * np.pi / 8, -np.pi / 4), (np.pi / 4, 3 * np.pi / 8)],
                    try_to_place_in="pan",
                ),
            )
        )

        cfgs.append(
            dict(
                name="container",
                obj_groups=("plate", "bowl"),
                placement=dict(
                    fixture=self.counter,
                    sample_region_kwargs=dict(
                        ref=self.stove,
                    ),
                    size=(0.30, 0.30),
                    pos=("ref", -1.0),
                ),
            )
        )

        return cfgs

    def _check_success(self):
        """
        Check if the stove to counter pick and place task is successful.
        Checks if the object is inside the container on the counter and the gripper far from the object.

        Returns:
            bool: True if the task is successful, False otherwise
        """
        obj_in_container = OU.check_obj_in_receptacle(self, "obj", "container", th=0.07)
        gripper_obj_far = OU.gripper_obj_far(self)

        return obj_in_container and gripper_obj_far
