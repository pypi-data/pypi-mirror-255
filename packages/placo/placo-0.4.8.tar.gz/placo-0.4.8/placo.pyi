import numpy
import typing
AvoidSelfCollisionsDynamicsConstraint = typing.NewType("AvoidSelfCollisionsDynamicsConstraint", None)
AvoidSelfCollisionsKinematicsConstraint = typing.NewType("AvoidSelfCollisionsKinematicsConstraint", None)
AxisAlignTask = typing.NewType("AxisAlignTask", None)
AxisesMask = typing.NewType("AxisesMask", None)
CentroidalMomentumTask = typing.NewType("CentroidalMomentumTask", None)
CoMPolygonConstraint = typing.NewType("CoMPolygonConstraint", None)
CoMTask = typing.NewType("CoMTask", None)
Collision = typing.NewType("Collision", None)
ConeConstraint = typing.NewType("ConeConstraint", None)
Contact = typing.NewType("Contact", None)
Contact6D = typing.NewType("Contact6D", None)
CubicSpline = typing.NewType("CubicSpline", None)
CubicSpline3D = typing.NewType("CubicSpline3D", None)
Distance = typing.NewType("Distance", None)
DistanceTask = typing.NewType("DistanceTask", None)
DynamicsCoMTask = typing.NewType("DynamicsCoMTask", None)
DynamicsConstraint = typing.NewType("DynamicsConstraint", None)
DynamicsFrameTask = typing.NewType("DynamicsFrameTask", None)
DynamicsGearTask = typing.NewType("DynamicsGearTask", None)
DynamicsJointsTask = typing.NewType("DynamicsJointsTask", None)
DynamicsOrientationTask = typing.NewType("DynamicsOrientationTask", None)
DynamicsPositionTask = typing.NewType("DynamicsPositionTask", None)
DynamicsReactionRatioConstraint = typing.NewType("DynamicsReactionRatioConstraint", None)
DynamicsRelativeFrameTask = typing.NewType("DynamicsRelativeFrameTask", None)
DynamicsRelativeOrientationTask = typing.NewType("DynamicsRelativeOrientationTask", None)
DynamicsRelativePositionTask = typing.NewType("DynamicsRelativePositionTask", None)
DynamicsSolver = typing.NewType("DynamicsSolver", None)
DynamicsSolverResult = typing.NewType("DynamicsSolverResult", None)
DynamicsTask = typing.NewType("DynamicsTask", None)
DynamicsTorqueTask = typing.NewType("DynamicsTorqueTask", None)
Exception = typing.NewType("Exception", None)
Expression = typing.NewType("Expression", None)
ExternalWrenchContact = typing.NewType("ExternalWrenchContact", None)
Flags = typing.NewType("Flags", None)
Footstep = typing.NewType("Footstep", None)
Footsteps = typing.NewType("Footsteps", None)
FootstepsPlanner = typing.NewType("FootstepsPlanner", None)
FootstepsPlannerNaive = typing.NewType("FootstepsPlannerNaive", None)
FootstepsPlannerRepetitive = typing.NewType("FootstepsPlannerRepetitive", None)
FrameTask = typing.NewType("FrameTask", None)
GearTask = typing.NewType("GearTask", None)
HumanoidParameters = typing.NewType("HumanoidParameters", None)
HumanoidRobot = typing.NewType("HumanoidRobot", None)
HumanoidRobot_Side = typing.NewType("HumanoidRobot_Side", None)
Integrator = typing.NewType("Integrator", None)
IntegratorTrajectory = typing.NewType("IntegratorTrajectory", None)
JointsTask = typing.NewType("JointsTask", None)
KinematicsConstraint = typing.NewType("KinematicsConstraint", None)
KinematicsSolver = typing.NewType("KinematicsSolver", None)
KineticEnergyRegularizationTask = typing.NewType("KineticEnergyRegularizationTask", None)
LIPM = typing.NewType("LIPM", None)
LIPMTrajectory = typing.NewType("LIPMTrajectory", None)
OrientationTask = typing.NewType("OrientationTask", None)
PointContact = typing.NewType("PointContact", None)
PolygonConstraint = typing.NewType("PolygonConstraint", None)
PositionTask = typing.NewType("PositionTask", None)
Prioritized = typing.NewType("Prioritized", None)
Problem = typing.NewType("Problem", None)
ProblemConstraint = typing.NewType("ProblemConstraint", None)
PuppetContact = typing.NewType("PuppetContact", None)
QPError = typing.NewType("QPError", None)
RegularizationTask = typing.NewType("RegularizationTask", None)
Relative6DContact = typing.NewType("Relative6DContact", None)
RelativeFrameTask = typing.NewType("RelativeFrameTask", None)
RelativeOrientationTask = typing.NewType("RelativeOrientationTask", None)
RelativePointContact = typing.NewType("RelativePointContact", None)
RelativePositionTask = typing.NewType("RelativePositionTask", None)
RobotWrapper = typing.NewType("RobotWrapper", None)
RobotWrapper_State = typing.NewType("RobotWrapper_State", None)
Sparsity = typing.NewType("Sparsity", None)
SparsityInterval = typing.NewType("SparsityInterval", None)
Support = typing.NewType("Support", None)
Supports = typing.NewType("Supports", None)
SwingFoot = typing.NewType("SwingFoot", None)
SwingFootCubic = typing.NewType("SwingFootCubic", None)
SwingFootCubicTrajectory = typing.NewType("SwingFootCubicTrajectory", None)
SwingFootQuintic = typing.NewType("SwingFootQuintic", None)
SwingFootQuinticTrajectory = typing.NewType("SwingFootQuinticTrajectory", None)
SwingFootTrajectory = typing.NewType("SwingFootTrajectory", None)
Task = typing.NewType("Task", None)
TaskContact = typing.NewType("TaskContact", None)
Variable = typing.NewType("Variable", None)
WalkPatternGenerator = typing.NewType("WalkPatternGenerator", None)
WalkTasks = typing.NewType("WalkTasks", None)
WalkTrajectory = typing.NewType("WalkTrajectory", None)
WheelTask = typing.NewType("WheelTask", None)
map_indexing_suite_map_string_double_entry = typing.NewType("map_indexing_suite_map_string_double_entry", None)
map_string_double = typing.NewType("map_string_double", None)
vector_Collision = typing.NewType("vector_Collision", None)
vector_Distance = typing.NewType("vector_Distance", None)
vector_MatrixXd = typing.NewType("vector_MatrixXd", None)
vector_Vector2d = typing.NewType("vector_Vector2d", None)
vector_Vector3d = typing.NewType("vector_Vector3d", None)
vector_double = typing.NewType("vector_double", None)
vector_int = typing.NewType("vector_int", None)
vector_string = typing.NewType("vector_string", None)
class AvoidSelfCollisionsDynamicsConstraint:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def configure(
    self: AvoidSelfCollisionsDynamicsConstraint,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  self_collisions_margin: float # double
  """Margin for self collisions [m]. 
        """

  self_collisions_trigger: float # double
  """Distance that triggers the constraint [m]. 
        """


class AvoidSelfCollisionsKinematicsConstraint:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def configure(
    self: AvoidSelfCollisionsKinematicsConstraint,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  self_collisions_margin: float # double
  """Margin for self collisions [m]. 
        """

  self_collisions_trigger: float # double
  """Distance that triggers the constraint [m]. 
        """


class AxisAlignTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    self: AxisAlignTask,
    frame_index: any, # pinocchio::FrameIndex
    axis_frame: numpy.ndarray, # Eigen::Vector3d
    targetAxis_world: numpy.ndarray, # Eigen::Vector3d

  ) -> any:
    ...

  axis_frame: numpy.ndarray # Eigen::Vector3d
  """Axis in the frame. 
        """

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: AxisAlignTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: AxisAlignTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: AxisAlignTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  frame_index: any # pinocchio::FrameIndex
  """Target frame. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  targetAxis_world: numpy.ndarray # Eigen::Vector3d
  """Target axis in the world. 
        """

  def update(
    self: AxisAlignTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class AxisesMask:
  """Used to mask some task axises. 
    """
  R_custom_world: numpy.ndarray # Eigen::Matrix3d
  """ROtation from world to custom rotation (provided by the user) 
        """

  R_local_world: numpy.ndarray # Eigen::Matrix3d
  """Rotation from world to local frame (provided by task) 
        """

  def __init__(
    self: AxisesMask,

  ) -> any:
    ...

  def apply(
    self: AxisesMask,
    M: numpy.ndarray, # Eigen::MatrixXd

  ) -> numpy.ndarray:
    """Apply the masking to a given matrix. 
        

    :param M: the matrix to be masked (3xn)"""
    ...

  def set_axises(
    self: AxisesMask,
    axises: str, # std::string
    frame: str, # std::string

  ) -> None:
    """Sets the axises to be masked (kept), for example "xy". 
        

    :param axises: axises to be kept 

    :param frame: the reference frame where the masking is done (task, local or custom)"""
    ...


class CentroidalMomentumTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  L_world: numpy.ndarray # Eigen::Vector3d
  """Target centroidal angular momentum in the world. 
        """

  def __init__(
    self: CentroidalMomentumTask,
    L_world: numpy.ndarray, # Eigen::Vector3d

  ) -> any:
    """See KinematicsSolver::add_centroidal_momentum_task."""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: CentroidalMomentumTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: CentroidalMomentumTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: CentroidalMomentumTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  mask: AxisesMask # placo::tools::AxisesMask
  """Axises mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def update(
    self: CentroidalMomentumTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class CoMPolygonConstraint:
  def __init__(
    self: CoMPolygonConstraint,
    polygon: list[numpy.ndarray], # const std::vector< Eigen::Vector2d > &
    margin: float = 0., # double

  ) -> any:
    """Ensures that the CoM (2D) lies inside the given polygon. 
        

    :param polygon: Clockwise polygon"""
    ...

  def configure(
    self: CoMPolygonConstraint,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  dcm: bool # bool
  """If set to true, the DCM will be used instead of the CoM. 
        """

  margin: float # double
  """Margin for the polygon constraint (minimum distance between the CoM and the polygon) 
        """

  name: str # std::string
  """Object name. 
        """

  omega: float # double
  """If DCM mode is enabled, the constraint will be applied on the DCM instead of the CoM with the following omega (sqrt(g / h)) 
        """

  polygon: list[numpy.ndarray] # std::vector< Eigen::Vector2d >
  """Clockwise polygon. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """


class CoMTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    self: CoMTask,
    target_world: numpy.ndarray, # Eigen::Vector3d

  ) -> any:
    """See KinematicsSolver::add_com_task."""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: CoMTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: CoMTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: CoMTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  target_world: numpy.ndarray # Eigen::Vector3d
  """Target for the CoM in the world. 
        """

  def update(
    self: CoMTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class Collision:
  """Represents a collision between two bodies. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  bodyA: str # std::string
  """Name of the body A. 
        """

  bodyB: str # std::string
  """Name of the body B. 
        """

  def get_contact(
    arg1: Collision,
    arg2: int,

  ) -> numpy.ndarray:
    ...

  objA: int # int
  """Index of object A in the collision geometry. 
        """

  objB: int # int
  """Index of object B in the collision geometry. 
        """

  parentA: any # pinocchio::JointIndex
  """The joint parent of body A. 
        """

  parentB: any # pinocchio::JointIndex
  """The joint parent of body B. 
        """


class ConeConstraint:
  """A cone constraint is a constraint where the z-axis of frame a and frame b should remaine within a cone of angle angle_max. 
    """
  N: int # int
  """Number of slices used to discretize the cone. 
        """

  def __init__(
    self: ConeConstraint,
    frame_a: any, # pinocchio::FrameIndex
    frame_b: any, # pinocchio::FrameIndex
    angle_max: float, # double

  ) -> any:
    """With a cone constraint, the z-axis of frame a and frame b should remaine within a cone of angle angle_max. 
        

    :param frame_a: 

    :param frame_b: 

    :param angle_max:"""
    ...

  angle_max: float # double
  """Maximum angle allowable by the cone constraint (between z-axis of frame_a and frame_b) 
        """

  def configure(
    self: ConeConstraint,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  range: float # double
  """Range of the cone discretization (in radians). The cone is discretized in [-range, range] around the current orientation. 
        """


class Contact:
  def __init__(
    self: Contact,

  ) -> any:
    ...

  active: bool # bool
  """true if the contact is active (ignored by the solver else, this allow to enable/disable a contact without removing it from the solver) 
        """

  mu: float # double
  """Coefficient of friction (if relevant) 
        """

  weight_forces: float # double
  """Weight of forces for the optimization (if relevant) 
        """

  weight_moments: float # double
  """Weight of moments for optimization (if relevant) 
        """

  wrench: numpy.ndarray # Eigen::VectorXd
  """Wrench populated after the DynamicsSolver::solve call. 
        """


class Contact6D:
  def __init__(
    self: Contact6D,
    frame_task: DynamicsFrameTask, # placo::dynamics::FrameTask
    unilateral: bool, # bool

  ) -> any:
    """see DynamicsSolver::add_fixed_planar_contact and DynamicsSolver::add_unilateral_planar_contact"""
    ...

  active: bool # bool
  """true if the contact is active (ignored by the solver else, this allow to enable/disable a contact without removing it from the solver) 
        """

  length: float # double
  """Rectangular contact length along local x-axis. 
        """

  mu: float # double
  """Coefficient of friction (if relevant) 
        """

  def orientation_task(
    self: Contact6D,

  ) -> DynamicsOrientationTask:
    """Associated orientation task."""
    ...

  def position_task(
    self: Contact6D,

  ) -> DynamicsPositionTask:
    """Associated position task."""
    ...

  unilateral: bool # bool
  """true for unilateral contact with the ground 
        """

  weight_forces: float # double
  """Weight of forces for the optimization (if relevant) 
        """

  weight_moments: float # double
  """Weight of moments for optimization (if relevant) 
        """

  width: float # double
  """Rectangular contact width along local y-axis. 
        """

  wrench: numpy.ndarray # Eigen::VectorXd
  """Wrench populated after the DynamicsSolver::solve call. 
        """

  def zmp(
    self: Contact6D,

  ) -> numpy.ndarray:
    """Returns the contact ZMP in the local frame. 
        

    :return: zmp"""
    ...


class CubicSpline:
  def __init__(
    self: CubicSpline,
    angular: bool = False, # bool

  ) -> any:
    ...

  def add_point(
    self: CubicSpline,
    t: float, # double
    x: float, # double
    dx: float, # double

  ) -> None:
    """Adds a point in the spline. 
        

    :param t: time 

    :param x: value 

    :param dx: speed"""
    ...

  def clear(
    self: CubicSpline,

  ) -> None:
    """Clears the spline."""
    ...

  def duration(
    self: CubicSpline,

  ) -> float:
    """Spline duration. 
        

    :return: duration in seconds"""
    ...

  def pos(
    self: CubicSpline,
    t: float, # double

  ) -> float:
    """Retrieve the position at a given time. 
        

    :param t: time 

    :return: position"""
    ...

  def vel(
    self: CubicSpline,
    x: float, # double

  ) -> float:
    """Retrieve velocity at a given time. 
        

    :param t: time 

    :return: velocity"""
    ...


class CubicSpline3D:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def add_point(
    self: CubicSpline3D,
    t: float, # double
    x: numpy.ndarray, # Eigen::Vector3d
    dx: numpy.ndarray, # Eigen::Vector3d

  ) -> None:
    """Adds a point. 
        

    :param t: time 

    :param x: value (3D vector) 

    :param dx: velocity (3D vector)"""
    ...

  def clear(
    self: CubicSpline3D,

  ) -> None:
    """Clears the spline."""
    ...

  def duration(
    self: CubicSpline3D,

  ) -> float:
    """Spline duration. 
        

    :return: spline duration in seconds"""
    ...

  def pos(
    self: CubicSpline3D,
    t: float, # double

  ) -> numpy.ndarray:
    """Returns the spline value at time t. 
        

    :param t: time 

    :return: position (3D vector)"""
    ...

  def vel(
    self: CubicSpline3D,
    t: float, # double

  ) -> numpy.ndarray:
    """Returns the spline velocity at time t. 
        

    :param t: time 

    :return: velocity (3D vector)"""
    ...


class Distance:
  """Represents a distance between two bodies. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  min_distance: float # double
  """Current minimum distance between the two objects. 
        """

  objA: int # int
  """Index of object A in the collision geometry. 
        """

  objB: int # int
  """Index of object B in the collision geometry. 
        """

  parentA: any # pinocchio::JointIndex
  """Parent joint of body A. 
        """

  parentB: any # pinocchio::JointIndex
  """Parent joint of body B. 
        """

  pointA: numpy.ndarray # Eigen::Vector3d
  """Point of object A considered. 
        """

  pointB: numpy.ndarray # Eigen::Vector3d
  """Point of object B considered. 
        """


class DistanceTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    self: DistanceTask,
    frame_a: any, # pinocchio::FrameIndex
    frame_b: any, # pinocchio::FrameIndex
    distance: float, # double

  ) -> any:
    """see KinematicsSolver::add_distance_task"""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: DistanceTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  distance: float # double
  """Target distance between A and B. 
        """

  def error(
    self: DistanceTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: DistanceTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  frame_a: any # pinocchio::FrameIndex
  """Frame A. 
        """

  frame_b: any # pinocchio::FrameIndex
  """Frame B. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def update(
    self: DistanceTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class DynamicsCoMTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  def __init__(
    arg1: object,
    arg2: numpy.ndarray,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsCoMTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  ddtarget_world: numpy.ndarray # Eigen::Vector3d
  """Target acceleration in the world. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  dtarget_world: numpy.ndarray # Eigen::Vector3d
  """Target velocity to reach in robot frame. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Axises mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  target_world: numpy.ndarray # Eigen::Vector3d
  """Target to reach in world frame. 
        """


class DynamicsConstraint:
  def __init__(

  ) -> any:
    ...

  def configure(
    self: DynamicsConstraint,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """


class DynamicsFrameTask:
  T_world_frame: any

  def __init__(
    arg1: object,

  ) -> None:
    ...

  def configure(
    self: DynamicsFrameTask,
    name: str, # std::string
    priority: str = "soft", # std::string
    position_weight: float = 1.0, # double
    orientation_weight: float = 1.0, # double

  ) -> None:
    """Configures the frame task. 
        

    :param name: task name 

    :param priority: task priority 

    :param position_weight: weight for the position task 

    :param orientation_weight: weight for the orientation task"""
    ...

  def orientation(
    self: DynamicsFrameTask,

  ) -> DynamicsOrientationTask:
    ...

  def position(
    self: DynamicsFrameTask,

  ) -> DynamicsPositionTask:
    ...


class DynamicsGearTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  def __init__(
    arg1: object,

  ) -> None:
    ...

  def add_gear(
    self: DynamicsGearTask,
    target: str, # std::string
    source: str, # std::string
    ratio: float, # double

  ) -> None:
    """Adds a gear constraint, you can add multiple source for the same target, they will be summed. 
        

    :param target: target joint 

    :param source: source joint 

    :param ratio: ratio"""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsGearTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def set_gear(
    self: DynamicsGearTask,
    target: str, # std::string
    source: str, # std::string
    ratio: float, # double

  ) -> None:
    """Sets a gear constraint. 
        

    :param target: target joint 

    :param source: source joint 

    :param ratio: ratio"""
    ...


class DynamicsJointsTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  def __init__(
    arg1: object,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsJointsTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def set_joint(
    self: DynamicsJointsTask,
    joint: str, # std::string
    target: float, # double
    velocity: float = 0., # double
    acceleration: float = 0., # double

  ) -> None:
    """Sets the target for a given joint. 
        

    :param joint: joint name 

    :param target: target position 

    :param velocity: target velocity 

    :param acceleration: target acceleration"""
    ...

  def set_joints(
    arg1: DynamicsJointsTask,
    arg2: dict,

  ) -> None:
    ...

  def set_joints_velocities(
    arg1: DynamicsJointsTask,
    arg2: dict,

  ) -> None:
    ...


class DynamicsOrientationTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  R_world_frame: numpy.ndarray # Eigen::Matrix3d
  """Target orientation. 
        """

  def __init__(
    arg1: object,
    arg2: int,
    arg3: numpy.ndarray,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsOrientationTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  domega_world: numpy.ndarray # Eigen::Vector3d
  """Target angular acceleration. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  omega_world: numpy.ndarray # Eigen::Vector3d
  """Target angular velocity. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """


class DynamicsPositionTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  def __init__(
    arg1: object,
    arg2: int,
    arg3: numpy.ndarray,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsPositionTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  dtarget_world: numpy.ndarray # Eigen::Vector3d
  """Target velocity in the world. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  frame_index: any # pinocchio::FrameIndex
  """Frame. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  target_world: numpy.ndarray # Eigen::Vector3d
  """Target position in the world. 
        """


class DynamicsReactionRatioConstraint:
  def __init__(
    arg1: object,
    arg2: Contact,
    arg3: float,

  ) -> None:
    ...

  def configure(
    self: DynamicsReactionRatioConstraint,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  reaction_ratio: float # double
  """Reaction ratio to be enforced. 
        """


class DynamicsRelativeFrameTask:
  T_a_b: any

  def __init__(
    arg1: object,

  ) -> None:
    ...

  def configure(
    self: DynamicsRelativeFrameTask,
    name: str, # std::string
    priority: str = "soft", # std::string
    position_weight: float = 1.0, # double
    orientation_weight: float = 1.0, # double

  ) -> None:
    """Configures the relative frame task. 
        

    :param name: task name 

    :param priority: task priority 

    :param position_weight: weight for the position task 

    :param orientation_weight: weight for the orientation task"""
    ...

  def orientation(
    self: DynamicsRelativeFrameTask,

  ) -> DynamicsRelativeOrientationTask:
    """Orientation task."""
    ...

  def position(
    self: DynamicsRelativeFrameTask,

  ) -> DynamicsRelativePositionTask:
    """Position task."""
    ...


class DynamicsRelativeOrientationTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  R_a_b: numpy.ndarray # Eigen::Matrix3d
  """Target relative orientation. 
        """

  def __init__(
    arg1: object,
    arg2: int,
    arg3: int,
    arg4: numpy.ndarray,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsRelativeOrientationTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  domega_a_b: numpy.ndarray # Eigen::Vector3d
  """Target relative angular velocity. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  omega_a_b: numpy.ndarray # Eigen::Vector3d
  """Target relative angular velocity. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """


class DynamicsRelativePositionTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  def __init__(
    arg1: object,
    arg2: int,
    arg3: int,
    arg4: numpy.ndarray,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsRelativePositionTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  ddtarget: numpy.ndarray # Eigen::Vector3d
  """Target relative velocity. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  dtarget: numpy.ndarray # Eigen::Vector3d
  """Target relative velocity. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  target: numpy.ndarray # Eigen::Vector3d
  """Target relative position. 
        """


class DynamicsSolver:
  def __init__(
    self: DynamicsSolver,
    robot: RobotWrapper, # placo::model::RobotWrapper

  ) -> any:
    ...

  def add_avoid_self_collisions_constraint(
    self: DynamicsSolver,

  ) -> AvoidSelfCollisionsDynamicsConstraint:
    """Adds a constraint to the solver. 
        

    :return: constraint"""
    ...

  def add_com_task(
    self: DynamicsSolver,
    target_world: numpy.ndarray, # Eigen::Vector3d

  ) -> DynamicsCoMTask:
    """Adds a center of mass (in the world) task. 
        

    :param target_world: target (in the world) 

    :return: center of mass task"""
    ...

  def add_constraint(
    self: DynamicsSolver,
    constraint: any, # T *

  ) -> any:
    """Adds a constraint to the solver. 
        

    :param constraint: constraint 

    :return: reference to internal constraint"""
    ...

  def add_external_wrench_contact(
    self: DynamicsSolver,
    frame_name: str, # std::string

  ) -> ExternalWrenchContact:
    """Adds an external wrench. 
        

    :param frame_name: frame 

    :return: external wrench contact"""
    ...

  def add_fixed_contact(
    self: DynamicsSolver,
    frame_task: DynamicsFrameTask, # placo::dynamics::FrameTask

  ) -> Contact6D:
    """Adds a fixed contact. 
        

    :param frame_task: the associated frame task 

    :return: fixed contact"""
    ...

  def add_frame_task(
    self: DynamicsSolver,
    frame_name: str, # std::string
    T_world_frame: numpy.ndarray, # Eigen::Affine3d

  ) -> DynamicsFrameTask:
    """Adds a frame task, which is a pseudo-task packaging position and orientation, resulting in a decoupled task. 
        

    :param frame_index: target frame 

    :param T_world_frame: target transformation in the world 

    :return: frame task"""
    ...

  def add_gear_task(
    self: DynamicsSolver,

  ) -> DynamicsGearTask:
    """Adds a gear task, allowing replication of a joint. This can be used to implement timing belt, if coupled with an internal force. 
        

    :return: gear task"""
    ...

  def add_joints_task(
    self: DynamicsSolver,

  ) -> DynamicsJointsTask:
    """Adds a joints task. 
        

    :return: joints task"""
    ...

  def add_orientation_task(
    self: DynamicsSolver,
    frame_name: str, # std::string
    R_world_frame: numpy.ndarray, # Eigen::Matrix3d

  ) -> DynamicsOrientationTask:
    """Adds an orientation (in the world) task. 
        

    :param frame_index: target frame 

    :param R_world_frame: target world orientation 

    :return: orientation task"""
    ...

  def add_planar_contact(
    self: DynamicsSolver,
    frame_task: DynamicsFrameTask, # placo::dynamics::FrameTask

  ) -> Contact6D:
    """Adds a planar contact, which is unilateral in the sense of the local body z-axis. 
        

    :param frame_task: associated frame task 

    :return: planar contact"""
    ...

  def add_point_contact(
    self: DynamicsSolver,
    position_task: DynamicsPositionTask, # placo::dynamics::PositionTask

  ) -> PointContact:
    """Adds a point contact. 
        

    :param position_task: the associated position task 

    :return: point contact"""
    ...

  def add_position_task(
    self: DynamicsSolver,
    frame_name: str, # std::string
    target_world: numpy.ndarray, # Eigen::Vector3d

  ) -> DynamicsPositionTask:
    """Adds a position (in the world) task. 
        

    :param frame_index: target frame 

    :param target_world: target position in the world 

    :return: position task"""
    ...

  def add_puppet_contact(
    self: DynamicsSolver,

  ) -> PuppetContact:
    """Adds a puppet contact, this will add some free contact forces for the whole system, allowing it to be controlled freely. 
        

    :return: puppet contact"""
    ...

  def add_reaction_ratio_constraint(
    self: DynamicsSolver,
    contact: Contact, # placo::dynamics::Contact
    reaction_ratio: float, # double

  ) -> DynamicsReactionRatioConstraint:
    """Adds a constraint enforce reaction ratio. 
        

    :param contact: contact 

    :param reaction_ratio: reaction ratio to enforce 

    :return: reaction ratio constraint"""
    ...

  def add_relative_fixed_contact(
    self: DynamicsSolver,
    frame_task: DynamicsRelativeFrameTask, # placo::dynamics::RelativeFrameTask

  ) -> Relative6DContact:
    """Adds a relative fixed contact, can be used for fixed closed loops. 
        

    :param frame_task: the associated relative frame task 

    :return: relative fixed contact"""
    ...

  def add_relative_frame_task(
    self: DynamicsSolver,
    frame_a_name: str, # std::string
    frame_b_name: str, # std::string
    T_a_b: numpy.ndarray, # Eigen::Affine3d

  ) -> DynamicsRelativeFrameTask:
    """Adds a relative frame task, which is a pseudo-task packaging relative position and orientation tasks. 
        

    :param frame_a_index: frame a 

    :param frame_b_index: frame b 

    :param T_a_b: target transformation value for b frame in a 

    :return: relative frame task"""
    ...

  def add_relative_orientation_task(
    self: DynamicsSolver,
    frame_a_name: str, # std::string
    frame_b_name: str, # std::string
    R_a_b: numpy.ndarray, # Eigen::Matrix3d

  ) -> DynamicsRelativeOrientationTask:
    """Adds a relative orientation task. 
        

    :param frame_a_index: frame a 

    :param frame_b_index: frame b 

    :param R_a_b: target value for the orientation of b frame in a 

    :return: relative orientation task"""
    ...

  def add_relative_point_contact(
    self: DynamicsSolver,
    position_task: DynamicsRelativePositionTask, # placo::dynamics::RelativePositionTask

  ) -> RelativePointContact:
    """Adds a relative point contact, which can be typically used for internal forces like loop-closing. 
        

    :param position_task: associated relative position task 

    :return: relative point contact"""
    ...

  def add_relative_position_task(
    self: DynamicsSolver,
    frame_a_name: str, # std::string
    frame_b_name: str, # std::string
    target_world: numpy.ndarray, # Eigen::Vector3d

  ) -> DynamicsRelativePositionTask:
    """Adds a relative position task. 
        

    :param frame_a_index: frame a 

    :param frame_b_index: frame b 

    :param target: target value for AB vector, expressed in A 

    :return: relative position task"""
    ...

  def add_task(
    self: DynamicsSolver,
    task: any, # T *

  ) -> any:
    """Adds a task to the solver. 
        

    :param task: task 

    :return: reference to internal task"""
    ...

  def add_task_contact(
    self: DynamicsSolver,
    task: DynamicsTask, # placo::dynamics::Task

  ) -> TaskContact:
    """Adds contact forces associated with any given task. 
        

    :param task: task 

    :return: task contact"""
    ...

  def add_torque_task(
    self: DynamicsSolver,

  ) -> DynamicsTorqueTask:
    """Adds a torque task. 
        

    :return: torque task"""
    ...

  def add_unilateral_point_contact(
    self: DynamicsSolver,
    position_task: DynamicsPositionTask, # placo::dynamics::PositionTask

  ) -> PointContact:
    """Adds an unilateral point contact, in the sense of the world z-axis. 
        

    :param position_task: the associated position task 

    :return: unilateral point contact"""
    ...

  def clear(
    self: DynamicsSolver,

  ) -> None:
    """Clears the internal tasks."""
    ...

  def count_contacts(
    arg1: DynamicsSolver,

  ) -> int:
    ...

  dt: float # double
  """Solver dt (seconds) 
        """

  def dump_status(
    self: DynamicsSolver,

  ) -> None:
    """Shows the tasks status."""
    ...

  def enable_joint_limits(
    self: DynamicsSolver,
    enable: bool, # bool

  ) -> None:
    """Enables/disables joint limits inequalities."""
    ...

  def enable_torque_limits(
    self: DynamicsSolver,
    enable: bool, # bool

  ) -> None:
    """Enables/disables torque limits inequalities."""
    ...

  def enable_velocity_limits(
    self: DynamicsSolver,
    enable: bool, # bool

  ) -> None:
    """Enables/disables joint velocity inequalities."""
    ...

  def enable_velocity_vs_torque_limits(
    self: DynamicsSolver,
    enable: bool, # bool

  ) -> None:
    """Enables the velocity vs torque inequalities."""
    ...

  friction: float # double
  """Global friction that is added to all the joints. 
        """

  def get_contact(
    arg1: DynamicsSolver,
    arg2: int,

  ) -> Contact:
    ...

  gravity_only: bool # bool
  """Use gravity only (no coriolis, no centrifugal) 
        """

  def mask_fbase(
    self: DynamicsSolver,
    masked: bool, # bool

  ) -> None:
    """Decides if the floating base should be masked."""
    ...

  problem: Problem # placo::problem::Problem
  """Instance of the problem. 
        """

  qdd_safe: float # double
  """The value of qdd safe. 
        """

  def remove_constraint(
    self: DynamicsSolver,
    constraint: DynamicsConstraint, # placo::dynamics::Constraint

  ) -> None:
    """Removes a constraint from the solver. 
        

    :param constraint: constraint"""
    ...

  def remove_contact(
    self: DynamicsSolver,
    contact: Contact, # placo::dynamics::Contact

  ) -> None:
    """Removes a contact from the solver. 
        

    :param contact:"""
    ...

  def remove_task(
    self: DynamicsSolver,
    task: DynamicsFrameTask, # placo::dynamics::FrameTask

  ) -> None:
    """Removes a frame task from the solver. 
        

    :param task: frame task"""
    ...

  def reset_joint(
    self: DynamicsSolver,
    joint_name: str, # const std::string &

  ) -> None:
    """Resets a given joint so that its torque is no longer overriden. 
        

    :param joint_name: the joint"""
    ...

  robot: RobotWrapper # placo::model::RobotWrapper

  def set_passive(
    self: DynamicsSolver,
    joint_name: str, # const std::string &
    kp: float = 0., # double
    kd: float = 0., # double

  ) -> None:
    """Sets a DoF as passive, the corresponding tau will be fixed in the equation of motion it can be purely passive joint or a spring-like behaviour. 
        

    :param joint_name: the joint 

    :param is_passive: true if the should the joint be passive 

    :param kp: kp gain if the joint is a spring (0 by default) 

    :param kd: kd gain if the joint is a spring (0 by default)"""
    ...

  def set_tau(
    self: DynamicsSolver,
    joint_name: str, # const std::string &
    tau: float, # double

  ) -> None:
    """Sets a custom torque to be applied by a given joint. 
        

    :param joint_name: the joint 

    :param tau: torque"""
    ...

  def solve(
    self: DynamicsSolver,
    integrate: bool = False, # bool

  ) -> DynamicsSolverResult:
    ...


class DynamicsSolverResult:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  qdd: numpy.ndarray # Eigen::VectorXd

  success: bool # bool

  tau: numpy.ndarray # Eigen::VectorXd

  def tau_dict(
    arg1: DynamicsSolverResult,
    arg2: RobotWrapper,

  ) -> dict:
    ...


class DynamicsTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  def __init__(

  ) -> any:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """


class DynamicsTorqueTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """A matrix in Ax = b, where x is the accelerations. 
        """

  def __init__(
    arg1: object,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """b vector in Ax = b, where x is the accelerations 
        """

  def configure(
    self: DynamicsTorqueTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  critically_damped: bool # bool
  """If this is true, kd will be computed from kp to have a critically damped system. 
        """

  derror: numpy.ndarray # Eigen::MatrixXd
  """Current velocity error vector. 
        """

  error: numpy.ndarray # Eigen::MatrixXd
  """Current error vector. 
        """

  kd: float # double
  """D gain for position control. 
        """

  kp: float # double
  """K gain for position control. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def set_torque(
    self: DynamicsTorqueTask,
    joint: str, # std::string
    torque: float, # double

  ) -> None:
    """Sets the target for a given joint. 
        

    :param joint: joint name 

    :param torque: target torque"""
    ...


class Exception:
  def __init__(
    arg1: object,
    arg2: str,

  ) -> None:
    ...

  message: any


class Expression:
  """An expression is a linear combination of decision variables of the form Ax + b that can be conveniently manipulated using operators. 
    """
  A: numpy.ndarray # Eigen::MatrixXd
  """Expression A matrix, in Ax + b. 
        """

  def __init__(
    self: Expression,
    other: Expression, # placo::problem::Expression

  ) -> any:
    ...

  b: numpy.ndarray # Eigen::VectorXd
  """Expression b vector, in Ax + b. 
        """

  def cols(
    self: Expression,

  ) -> int:
    """Number of cols in A. 
        

    :return: number of cols in A"""
    ...

  @staticmethod
  def from_double(
    value: float, # const double &

  ) -> Expression:
    """Builds an expression from a double (A will be zero, the expression is only one row) 
        

    :param value: value 

    :return: expression"""
    ...

  @staticmethod
  def from_vector(
    v: numpy.ndarray, # const Eigen::VectorXd &

  ) -> Expression:
    """Builds an expression from a vector (A will be zeros) 
        

    :param v: vector 

    :return: expression"""
    ...

  def is_scalar(
    self: Expression,

  ) -> bool:
    """checks if the expression is a scalar 
        

    :return: true if the expression is a scalar"""
    ...

  def mean(
    self: Expression,

  ) -> Expression:
    """Reduces a multi-rows expression to the mean of its items. 
        

    :return: expression"""
    ...

  def multiply(
    self: Expression,
    M: numpy.ndarray, # const Eigen::MatrixXd

  ) -> Expression:
    """Multiply an expression on the left by a given matrix M. 
        

    :param M: matrix 

    :return: expression"""
    ...

  def piecewise_add(
    self: Expression,
    f: float, # double

  ) -> Expression:
    """Adds the expression element by element to another expression. 
        

    :param f: 

    :return:"""
    ...

  def rows(
    self: Expression,

  ) -> int:
    """Number of rows in A. 
        

    :return: number of rows in A"""
    ...

  def slice(
    self: Expression,
    start: int, # int
    rows: int = -1, # int

  ) -> Expression:
    """Slice rows from a given expression. 
        

    :param start: start row 

    :param rows: number of rows (default: -1, all rows) 

    :return: a sliced expression"""
    ...

  def sum(
    self: Expression,

  ) -> Expression:
    """Reduces a multi-rows expression to the sum of its items. 
        

    :return: expression"""
    ...

  def value(
    self: Expression,
    x: numpy.ndarray, # Eigen::VectorXd

  ) -> numpy.ndarray:
    """Retrieve the expression value, given a decision variable. This can be used after a problem is solved to retrieve a specific expression value. 
        

    :param x: 

    :return:"""
    ...


class ExternalWrenchContact:
  def __init__(
    self: ExternalWrenchContact,
    frame_index: any, # pinocchio::FrameIndex

  ) -> any:
    """see DynamicsSolver::add_external_wrench_contact"""
    ...

  active: bool # bool
  """true if the contact is active (ignored by the solver else, this allow to enable/disable a contact without removing it from the solver) 
        """

  frame_index: any # pinocchio::FrameIndex

  mu: float # double
  """Coefficient of friction (if relevant) 
        """

  w_ext: numpy.ndarray # Eigen::VectorXd

  weight_forces: float # double
  """Weight of forces for the optimization (if relevant) 
        """

  weight_moments: float # double
  """Weight of moments for optimization (if relevant) 
        """

  wrench: numpy.ndarray # Eigen::VectorXd
  """Wrench populated after the DynamicsSolver::solve call. 
        """


class Flags:
  def __init__(

  ) -> any:
    ...

  def as_integer_ratio(

  ) -> any:
    ...

  def bit_count(

  ) -> any:
    ...

  def bit_length(

  ) -> any:
    ...

  collision_as_visual: any

  def conjugate(

  ) -> any:
    ...

  denominator: any

  def from_bytes(

  ) -> any:
    ...

  ignore_collisions: any

  imag: any

  name: any

  names: any

  numerator: any

  real: any

  def to_bytes(

  ) -> any:
    ...

  values: any


class Footstep:
  """A footstep is the position of a specific foot on the ground. 
    """
  def __init__(
    self: Footstep,
    foot_width: float, # double
    foot_length: float, # double

  ) -> any:
    ...

  foot_length: float # double

  foot_width: float # double

  frame: numpy.ndarray # Eigen::Affine3d

  kick: bool # bool

  def overlap(
    self: Footstep,
    other: Footstep, # placo::humanoid::FootstepsPlanner::Footstep
    margin: float = 0., # double

  ) -> bool:
    ...

  @staticmethod
  def polygon_contains(
    polygon: list[numpy.ndarray], # std::vector< Eigen::Vector2d > &
    point: numpy.ndarray, # Eigen::Vector2d

  ) -> bool:
    ...

  side: any # placo::humanoid::HumanoidRobot::Side

  def support_polygon(
    self: Footstep,

  ) -> list[numpy.ndarray]:
    ...


class Footsteps:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: Footsteps,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: Footsteps,
    arg2: object,

  ) -> None:
    ...


class FootstepsPlanner:
  def __init__(
    self: FootstepsPlanner,
    parameters: HumanoidParameters, # placo::humanoid::HumanoidParameters

  ) -> any:
    """Initializes the solver. 
        

    :param parameters: Parameters of the walk"""
    ...

  @staticmethod
  def add_first_support(
    supports: list[Support], # std::vector<placo::humanoid::FootstepsPlanner::Support>
    support: Support, # placo::humanoid::FootstepsPlanner::Support

  ) -> None:
    ...

  @staticmethod
  def make_supports(
    footsteps: list[Footstep], # std::vector<placo::humanoid::FootstepsPlanner::Footstep>
    start: bool = True, # bool
    middle: bool = False, # bool
    end: bool = True, # bool

  ) -> list[Support]:
    """Generate the supports from the footsteps. 
        

    :param start: should we add a double support at the begining of the move? 

    :param middle: should we add a double support between each step ? 

    :param end: should we add a double support at the end of the move? 

    :return: vector of supports to use. It starts with initial double supports, and add double support phases between footsteps."""
    ...

  def opposite_footstep(
    self: FootstepsPlanner,
    footstep: Footstep, # placo::humanoid::FootstepsPlanner::Footstep
    d_x: float = 0., # double
    d_y: float = 0., # double
    d_theta: float = 0., # double

  ) -> Footstep:
    """Return the opposite footstep in a neutral position (i.e. at a distance parameters.feet_spacing from the given footstep)"""
    ...


class FootstepsPlannerNaive:
  def __init__(
    self: FootstepsPlannerNaive,
    parameters: HumanoidParameters, # placo::humanoid::HumanoidParameters

  ) -> any:
    ...

  @staticmethod
  def add_first_support(
    supports: list[Support], # std::vector<placo::humanoid::FootstepsPlanner::Support>
    support: Support, # placo::humanoid::FootstepsPlanner::Support

  ) -> None:
    ...

  def configure(
    self: FootstepsPlannerNaive,
    T_world_left_target: numpy.ndarray, # Eigen::Affine3d
    T_world_right_target: numpy.ndarray, # Eigen::Affine3d

  ) -> None:
    """Configure the naive footsteps planner. 
        

    :param T_world_left_target: Targetted frame for the left foot 

    :param T_world_right_target: Targetted frame for the right foot"""
    ...

  @staticmethod
  def make_supports(
    footsteps: list[Footstep], # std::vector<placo::humanoid::FootstepsPlanner::Footstep>
    start: bool = True, # bool
    middle: bool = False, # bool
    end: bool = True, # bool

  ) -> list[Support]:
    """Generate the supports from the footsteps. 
        

    :param start: should we add a double support at the begining of the move? 

    :param middle: should we add a double support between each step ? 

    :param end: should we add a double support at the end of the move? 

    :return: vector of supports to use. It starts with initial double supports, and add double support phases between footsteps."""
    ...

  def opposite_footstep(
    self: FootstepsPlannerNaive,
    footstep: Footstep, # placo::humanoid::FootstepsPlanner::Footstep
    d_x: float = 0., # double
    d_y: float = 0., # double
    d_theta: float = 0., # double

  ) -> Footstep:
    """Return the opposite footstep in a neutral position (i.e. at a distance parameters.feet_spacing from the given footstep)"""
    ...

  def plan(
    self: FootstepsPlannerNaive,
    flying_side: any, # placo::humanoid::HumanoidRobot::Side
    T_world_left: numpy.ndarray, # Eigen::Affine3d
    T_world_right: numpy.ndarray, # Eigen::Affine3d

  ) -> list[Footstep]:
    """Generate the footsteps. 
        

    :param flying_side: first step side 

    :param T_world_left: frame of the initial left foot 

    :param T_world_right: frame of the initial right foot"""
    ...


class FootstepsPlannerRepetitive:
  def __init__(
    self: FootstepsPlannerRepetitive,
    parameters: HumanoidParameters, # placo::humanoid::HumanoidParameters

  ) -> any:
    ...

  @staticmethod
  def add_first_support(
    supports: list[Support], # std::vector<placo::humanoid::FootstepsPlanner::Support>
    support: Support, # placo::humanoid::FootstepsPlanner::Support

  ) -> None:
    ...

  def configure(
    self: FootstepsPlannerRepetitive,
    x: float, # double
    y: float, # double
    theta: float, # double
    steps: int, # int

  ) -> None:
    """Compute the next footsteps based on coordinates expressed in the support frame laterally translated of +/- feet_spacing. 
        

    :param x: Longitudinal distance 

    :param y: Lateral distance 

    :param theta: Angle 

    :param steps: Number of steps"""
    ...

  @staticmethod
  def make_supports(
    footsteps: list[Footstep], # std::vector<placo::humanoid::FootstepsPlanner::Footstep>
    start: bool = True, # bool
    middle: bool = False, # bool
    end: bool = True, # bool

  ) -> list[Support]:
    """Generate the supports from the footsteps. 
        

    :param start: should we add a double support at the begining of the move? 

    :param middle: should we add a double support between each step ? 

    :param end: should we add a double support at the end of the move? 

    :return: vector of supports to use. It starts with initial double supports, and add double support phases between footsteps."""
    ...

  def opposite_footstep(
    self: FootstepsPlannerRepetitive,
    footstep: Footstep, # placo::humanoid::FootstepsPlanner::Footstep
    d_x: float = 0., # double
    d_y: float = 0., # double
    d_theta: float = 0., # double

  ) -> Footstep:
    """Return the opposite footstep in a neutral position (i.e. at a distance parameters.feet_spacing from the given footstep)"""
    ...

  def plan(
    self: FootstepsPlannerRepetitive,
    flying_side: any, # placo::humanoid::HumanoidRobot::Side
    T_world_left: numpy.ndarray, # Eigen::Affine3d
    T_world_right: numpy.ndarray, # Eigen::Affine3d

  ) -> list[Footstep]:
    """Generate the footsteps. 
        

    :param flying_side: first step side 

    :param T_world_left: frame of the initial left foot 

    :param T_world_right: frame of the initial right foot"""
    ...


class FrameTask:
  T_world_frame: any

  def __init__(
    self: FrameTask,
    position: PositionTask, # placo::kinematics::PositionTask
    orientation: OrientationTask, # placo::kinematics::OrientationTask

  ) -> any:
    """see KinematicsSolver::add_frame_task"""
    ...

  def configure(
    self: FrameTask,
    name: str, # std::string
    priority: str = "soft", # std::string
    position_weight: float = 1.0, # double
    orientation_weight: float = 1.0, # double

  ) -> None:
    """Configures the frame task. 
        

    :param name: task name 

    :param priority: task priority 

    :param position_weight: weight for the position task 

    :param orientation_weight: weight for the orientation task"""
    ...

  def orientation(
    self: FrameTask,

  ) -> OrientationTask:
    """Orientation task."""
    ...

  def position(
    self: FrameTask,

  ) -> PositionTask:
    """Position task."""
    ...


class GearTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    self: GearTask,

  ) -> any:
    """see KinematicsSolver::add_gear_task"""
    ...

  def add_gear(
    self: GearTask,
    target: str, # std::string
    source: str, # std::string
    ratio: float, # double

  ) -> None:
    """Adds a gear constraint, you can add multiple source for the same target, they will be summed. 
        

    :param target: target joint 

    :param source: source joint 

    :param ratio: ratio"""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: GearTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: GearTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: GearTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def set_gear(
    self: GearTask,
    target: str, # std::string
    source: str, # std::string
    ratio: float, # double

  ) -> None:
    """Sets a gear constraint. 
        

    :param target: target joint 

    :param source: source joint 

    :param ratio: ratio"""
    ...

  def update(
    self: GearTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class HumanoidParameters:
  """A collection of parameters that can be used to define the capabilities and the constants behind planning and control of an humanoid robot. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def double_support_duration(
    self: HumanoidParameters,

  ) -> float:
    """Duratuon [s]of a double support."""
    ...

  double_support_ratio: float # double
  """Duration ratio between single support and double support. 
        """

  def double_support_timesteps(
    self: HumanoidParameters,

  ) -> int:
    """Duration [timesteps] of a double support."""
    ...

  def dt(
    self: HumanoidParameters,

  ) -> float:
    """dt for planning [s]"""
    ...

  def ellipsoid_clip(
    self: HumanoidParameters,
    step: numpy.ndarray, # Eigen::Vector3d

  ) -> numpy.ndarray:
    """Applies the ellipsoid clipping to a given step size (dx, dy, dtheta)"""
    ...

  feet_spacing: float # double
  """Lateral spacing between feet [m]. 
        """

  foot_length: float # double
  """Foot length [m]. 
        """

  foot_width: float # double
  """Foot width [m]. 
        """

  foot_zmp_target_x: float # double
  """Target offset for the ZMP x reference trajectory in the foot frame [m]. 
        """

  foot_zmp_target_y: float # double
  """Target offset for the ZMP x reference trajectory in the foot frame, positive is "outward" [m]. 
        """

  def has_double_support(
    self: HumanoidParameters,

  ) -> bool:
    """Checks if the walk resulting from those parameters will have double supports."""
    ...

  def kick_support_duration(
    self: HumanoidParameters,

  ) -> float:
    """Duration [s] of a kick support."""
    ...

  kick_support_ratio: float # double
  """Duration ratio between single support and kick support. 
        """

  def kick_support_timesteps(
    self: HumanoidParameters,

  ) -> int:
    """Duration [timesteps]of a kick support."""
    ...

  planned_timesteps: int # int
  """Planning horizon for the CoM trajectory. 
        """

  replan_timesteps: int # int
  """Number of timesteps between each replan. Support phases have to last longer than [replan_frequency * dt] or their duration has to be equal to 0. 
        """

  single_support_duration: float # double
  """SSP duration [s]. 
        """

  single_support_timesteps: int # int
  """Number of timesteps for one single support. 
        """

  def startend_double_support_duration(
    self: HumanoidParameters,

  ) -> float:
    """Duration [s] of a start/end double support."""
    ...

  startend_double_support_ratio: float # double
  """Duration ratio between single support and double support. 
        """

  def startend_double_support_timesteps(
    self: HumanoidParameters,

  ) -> int:
    """Duration [timesteps]of a start/end double support."""
    ...

  walk_com_height: float # double
  """Target CoM height while walking [m]. 
        """

  walk_dtheta_spacing: float # double
  """How much we need to space the feet per dtheta [m/rad]. 
        """

  walk_foot_height: float # double
  """How height the feet are rising while walking [m]. 
        """

  walk_foot_rise_ratio: float # double
  """ratio of time spent at foot height during the step 
        """

  walk_max_dtheta: float # double
  """Maximum step (yaw) 
        """

  walk_max_dx_backward: float # double
  """Maximum step (backward) 
        """

  walk_max_dx_forward: float # double
  """Maximum step (forward) 
        """

  walk_max_dy: float # double
  """Maximum step (lateral) 
        """

  walk_trunk_pitch: float # double
  """Trunk pitch while walking [rad]. 
        """

  zmp_margin: float # double
  """Margin for the ZMP to live in the support polygon [m]. 
        """

  zmp_reference_weight: float # double
  """Weight for ZMP reference in the solver. 
        """


class HumanoidRobot:
  T_world_support: numpy.ndarray # Eigen::Affine3d
  """Transformation from support to world. 
        """

  def __init__(
    self: HumanoidRobot,
    model_directory: str = "robot", # std::string
    flags: int = 0, # int
    urdf_content: str = "", # std::string

  ) -> any:
    ...

  collision_model: any # pinocchio::GeometryModel
  """Pinocchio collision model. 
        """

  def com_jacobian(
    self: HumanoidRobot,

  ) -> any:
    """Jacobian of the CoM position expressed in the world. 
        

    :return: jacobian (3 x n matrix)"""
    ...

  def com_jacobian_time_variation(
    self: HumanoidRobot,

  ) -> any:
    """Jacobian time variation of the CoM expressed in the world. 
        

    :return: jacobian (3 x n matrix)"""
    ...

  def com_world(
    self: HumanoidRobot,

  ) -> numpy.ndarray:
    """Gets the CoM position in the world."""
    ...

  def dcm(
    self: HumanoidRobot,
    com_velocity: numpy.ndarray, # Eigen::Vector2d
    omega: float, # double

  ) -> numpy.ndarray:
    """Compute the Divergent Component of Motion (DCM) 
        

    :param com_velocity: CoM velocity 

    :param omega: Natural frequency of the LIP (= sqrt(g/h)) 

    :return: DCM"""
    ...

  def distances(
    self: HumanoidRobot,

  ) -> list[Distance]:
    """Computes all minimum distances between current collision pairs. 
        

    :return: vector of Distance"""
    ...

  def ensure_on_floor(
    self: HumanoidRobot,

  ) -> None:
    """Place the robot on its support on the floor."""
    ...

  def frame_jacobian(
    self: HumanoidRobot,
    frame: str, # const std::string &
    reference: str = "local_world_aligned", # const std::string &

  ) -> numpy.ndarray:
    """Frame jacobian, default reference is LOCAL_WORLD_ALIGNED. 
        

    :param frame: the frame for which we want the jacobian 

    :return: jacobian (6 x nv matrix), where nv is the size of qd"""
    ...

  def frame_jacobian_time_variation(
    self: HumanoidRobot,
    frame: str, # const std::string &
    reference: str = "local_world_" "aligned", # const std::string &

  ) -> numpy.ndarray:
    """Jacobian time variation $\dot J$, default reference is LOCAL_WORLD_ALIGNED. 
        

    :param frame: the frame for which we want the jacobian time variation 

    :param reference: the reference frame 

    :return: jacobian time variation (6 x nv matrix), where nv is the size of qd"""
    ...

  def frame_names(
    self: HumanoidRobot,

  ) -> list[str]:
    """All the frame names."""
    ...

  def generalized_gravity(
    self: HumanoidRobot,

  ) -> numpy.ndarray:
    """Computes generalized gravity."""
    ...

  def get_T_a_b(
    self: HumanoidRobot,
    frame_a: str, # const std::string &
    frame_b: str, # const std::string &

  ) -> numpy.ndarray:
    """Gets the transformation matrix from frame b to a. 
        

    :param frame_a: frame a 

    :param frame_b: frame b 

    :return: transformation"""
    ...

  def get_T_world_fbase(
    self: HumanoidRobot,

  ) -> numpy.ndarray:
    """Returns the transformation matrix from the fbase frame (which is the root of the URDF) to the world. 
        

    :return: transformation"""
    ...

  def get_T_world_frame(
    self: HumanoidRobot,
    frame: str, # const std::string &

  ) -> numpy.ndarray:
    """Gets the frame to world transformation matrix for a given frame. 
        

    :param frame: frame 

    :return: transformation"""
    ...

  def get_T_world_left(
    self: HumanoidRobot,

  ) -> numpy.ndarray:
    ...

  def get_T_world_right(
    self: HumanoidRobot,

  ) -> numpy.ndarray:
    ...

  def get_T_world_trunk(
    self: HumanoidRobot,

  ) -> numpy.ndarray:
    ...

  def get_com_velocity(
    self: HumanoidRobot,
    support: any, # placo::humanoid::HumanoidRobot::Side
    omega_b: numpy.ndarray, # Eigen::Vector3d

  ) -> numpy.ndarray:
    """Compute the center of mass velocity from the speed of the motors and the orientation of the trunk. 
        

    :param support: Support side 

    :param omega_b: Trunk angular velocity in the body frame 

    :return: Center of mass velocity"""
    ...

  def get_joint(
    self: HumanoidRobot,
    name: str, # const std::string &

  ) -> float:
    """Retrieves a joint value from state.q. 
        

    :param name: joint name 

    :return: the joint current (inner state) value (e.g rad for revolute or meters for prismatic)"""
    ...

  def get_joint_acceleration(
    self: HumanoidRobot,
    name: str, # const std::string &

  ) -> float:
    """Gets the joint acceleration from state.qd. 
        

    :param name: joint name 

    :return: joint acceleration"""
    ...

  def get_joint_offset(
    self: HumanoidRobot,
    name: str, # const std::string &

  ) -> int:
    """Gets the offset for a given joint in the state (in State::q) 
        

    :param name: joint name 

    :return: offset in state.q"""
    ...

  def get_joint_v_offset(
    self: HumanoidRobot,
    name: str, # const std::string &

  ) -> int:
    """Gets the offset for a given joint in the state (in State::qd and State::qdd) 
        

    :param name: joint name 

    :return: offset in state.qd and state.qdd"""
    ...

  def get_joint_velocity(
    self: HumanoidRobot,
    name: str, # const std::string &

  ) -> float:
    """Gets the joint velocity from state.qd. 
        

    :param name: joint name 

    :return: joint velocity"""
    ...

  def get_support_side(
    arg1: HumanoidRobot,

  ) -> HumanoidRobot_Side:
    ...

  def get_torques(
    self: HumanoidRobot,
    acc_a: numpy.ndarray, # Eigen::VectorXd
    contact_forces: numpy.ndarray, # Eigen::VectorXd
    use_non_linear_effects: bool = False, # bool

  ) -> numpy.ndarray:
    """Compute the torques of the motors from the contact forces. 
        

    :param acc_a: Accelerations of the actuated DoFs 

    :param contact_forces: Contact forces from the feet (forces are supposed normal to the ground) 

    :param use_non_linear_effects: If true, non linear effects are taken into account (state.qd necessary) 

    :return: Torques of the motors"""
    ...

  def get_torques_dict(
    arg1: HumanoidRobot,
    arg2: numpy.ndarray,
    arg3: numpy.ndarray,
    arg4: bool,

  ) -> dict:
    ...

  def integrate(
    self: HumanoidRobot,
    dt: float, # double

  ) -> None:
    """Integrates the internal state for a given dt 
        

    :param dt: delta time for integration expressed in seconds"""
    ...

  def joint_jacobian(
    self: HumanoidRobot,
    joint: str, # const std::string &
    reference: str = "local_world_aligned", # const std::string &

  ) -> numpy.ndarray:
    ...

  def joint_names(
    self: HumanoidRobot,
    include_floating_base: bool = False, # bool

  ) -> list[str]:
    """All the joint names. 
        

    :param include_floating_base: whether to include the floating base joint (false by default)"""
    ...

  def load_collision_pairs(
    self: HumanoidRobot,
    filename: str, # const std::string &

  ) -> None:
    """Loads collision pairs from a given JSON file. 
        

    :param filename: path to collisions.json file"""
    ...

  def make_solver(
    arg1: HumanoidRobot,

  ) -> KinematicsSolver:
    ...

  def mass_matrix(
    self: HumanoidRobot,

  ) -> numpy.ndarray:
    """Computes the mass matrix."""
    ...

  model: any # pinocchio::Model
  """Pinocchio model. 
        """

  def neutral_state(
    self: HumanoidRobot,

  ) -> RobotWrapper_State:
    """builds a neutral state (neutral position, zero speed) 
        

    :return: the state"""
    ...

  def non_linear_effects(
    self: HumanoidRobot,

  ) -> numpy.ndarray:
    """Computes non-linear effects (Corriolis, centrifual and gravitationnal effects)"""
    ...

  @staticmethod
  def other_side(
    side: any, # placo::humanoid::HumanoidRobot::Side

  ) -> any:
    ...

  def relative_position_jacobian(
    self: HumanoidRobot,
    frame_a: str, # const std::string &
    frame_b: str, # const std::string &

  ) -> numpy.ndarray:
    """Jacobian of the relative position of the position of b expressed in a. 
        

    :param frame_a: frame A 

    :param frame_b: frame B 

    :return: relative position jacobian of b expressed in a (3 x n matrix)"""
    ...

  def reset(
    self: HumanoidRobot,

  ) -> None:
    """Reset internal states, this sets q to the neutral position, qd and qdd to zero."""
    ...

  def self_collisions(
    self: HumanoidRobot,
    stop_at_first: bool = False, # bool

  ) -> list[Collision]:
    """Finds the self collision in current state, if stop_at_first is true, it will stop at the first collision found. 
        

    :param stop_at_first: whether to stop at the first collision found 

    :return: a vector of Collision"""
    ...

  def set_T_world_fbase(
    self: HumanoidRobot,
    T_world_fbase: numpy.ndarray, # Eigen::Affine3d

  ) -> None:
    """Updates the floating base to match the given transformation matrix. 
        

    :param T_world_fbase: transformation matrix"""
    ...

  def set_T_world_frame(
    self: HumanoidRobot,
    frame: str, # const std::string &
    T_world_frameTarget: numpy.ndarray, # Eigen::Affine3d

  ) -> None:
    """Updates the floating base status so that the given frame has the given transformation matrix. 
        

    :param frame: frame to update 

    :param T_world_frameTarget: transformation matrix"""
    ...

  def set_gravity(
    self: HumanoidRobot,
    gravity: numpy.ndarray, # Eigen::Vector3d

  ) -> None:
    """Sets the gravity vector."""
    ...

  def set_joint(
    self: HumanoidRobot,
    name: str, # const std::string &
    value: float, # double

  ) -> None:
    """Sets the value of a joint in state.q. 
        

    :param name: joint name 

    :param value: joint value (e.g rad for revolute or meters for prismatic)"""
    ...

  def set_joint_acceleration(
    self: HumanoidRobot,
    name: str, # const std::string &
    value: float, # double

  ) -> None:
    """Sets the joint acceleration in state.qd. 
        

    :param name: joint name 

    :param value: joint acceleration"""
    ...

  def set_joint_limits(
    self: HumanoidRobot,
    name: str, # const std::string &
    lower: float, # double
    upper: float, # double

  ) -> None:
    """Sets the limits for a given joint. 
        

    :param name: joint name 

    :param lower: lower limit 

    :param upper: upper limit"""
    ...

  def set_joint_velocity(
    self: HumanoidRobot,
    name: str, # const std::string &
    value: float, # double

  ) -> None:
    """Sets the joint velocity in state.qd. 
        

    :param name: joint name 

    :param value: joint velocity"""
    ...

  def set_torque_limit(
    self: HumanoidRobot,
    name: str, # const std::string &
    limit: float, # double

  ) -> None:
    """Sets the torque limit for a given joint. 
        

    :param name: joint name 

    :param limit: torque limit"""
    ...

  def set_velocity_limit(
    self: HumanoidRobot,
    name: str, # const std::string &
    limit: float, # double

  ) -> None:
    """Sets the velocity limit for a given joint. 
        

    :param name: joint name 

    :param limit: joint limit"""
    ...

  def set_velocity_limits(
    self: HumanoidRobot,
    limit: float, # double

  ) -> None:
    """Set the velocity limits for all the joints. 
        

    :param limit: limit"""
    ...

  state: RobotWrapper_State # placo::model::RobotWrapper::State
  """Robot's current state. 
        """

  def static_gravity_compensation_torques(
    self: HumanoidRobot,
    frame: str, # std::string

  ) -> numpy.ndarray:
    """Computes torques needed by the robot to compensate for the generalized gravity, assuming that the given frame is the (only) contact supporting the robot. 
        

    :param frame: frame"""
    ...

  def static_gravity_compensation_torques_dict(
    arg1: HumanoidRobot,
    arg2: str,

  ) -> dict:
    ...

  support_is_both: bool # bool
  """Are both feet supporting the robot. 
        """

  def torques_from_acceleration_with_fixed_frame(
    self: HumanoidRobot,
    qdd_a: numpy.ndarray, # Eigen::VectorXd
    fixed_frame: str, # std::string

  ) -> numpy.ndarray:
    """Computes required torques in the robot DOFs for a given acceleration of the actuated DOFs, assuming that the given frame is fixed. 
        

    :param qdd_a: acceleration of the actuated DOFs 

    :param fixed_frame: frame"""
    ...

  def torques_from_acceleration_with_fixed_frame_dict(
    arg1: HumanoidRobot,
    arg2: numpy.ndarray,
    arg3: str,

  ) -> dict:
    ...

  def total_mass(
    self: HumanoidRobot,

  ) -> float:
    """Total mass."""
    ...

  def update_kinematics(
    self: HumanoidRobot,

  ) -> None:
    """Update internal computation for kinematics (frames, jacobian). This method should be called when the robot state has changed."""
    ...

  def update_support_side(
    self: HumanoidRobot,
    side: str, # const std::string &

  ) -> None:
    ...

  visual_model: any # pinocchio::GeometryModel
  """Pinocchio visual model. 
        """

  def zmp(
    self: HumanoidRobot,
    com_acceleration: numpy.ndarray, # Eigen::Vector2d
    omega: float, # double

  ) -> numpy.ndarray:
    """Compute the Zero-tilting Moment Point (ZMP) 
        

    :param com_acceleration: CoM acceleration 

    :param omega: Natural frequency of the LIP (= sqrt(g/h)) 

    :return: ZMP"""
    ...


class HumanoidRobot_Side:
  def __init__(

  ) -> any:
    ...

  def as_integer_ratio(

  ) -> any:
    ...

  def bit_count(

  ) -> any:
    ...

  def bit_length(

  ) -> any:
    ...

  def conjugate(

  ) -> any:
    ...

  denominator: any

  def from_bytes(

  ) -> any:
    ...

  imag: any

  left: any

  name: any

  names: any

  numerator: any

  real: any

  right: any

  def to_bytes(

  ) -> any:
    ...

  values: any


class Integrator:
  """Integrator can be used to efficiently build expressions and values over a decision variable that is integrated over time with a given linear system. 
    """
  A: numpy.ndarray # Eigen::MatrixXd
  """The discrete system matrix such that $X_{k+1} = A X_k + B u_k$. 
        """

  B: numpy.ndarray # Eigen::MatrixXd
  """The discrete system matrix such that $X_{k+1} = A X_k + B u_k$. 
        """

  M: numpy.ndarray # Eigen::MatrixXd
  """The continuous system matrix. 
        """

  def __init__(
    self: Integrator,
    variable: Variable, # placo::problem::Variable
    X0: numpy.ndarray, # Eigen::VectorXd
    order: int, # int
    dt: float, # double

  ) -> any:
    """Creates an integrator able to build expressions and values over a decision variable. With this constructor, a continuous system matrix will be used (see below) 
        

    :param variable: variable to integrate 

    :param X0: x0 (initial state) 

    :param order: order 

    :param dt: delta time"""
    ...

  def expr(
    self: Integrator,
    step: int, # int
    diff: int = -1, # int

  ) -> Expression:
    """Builds an expression for the given step and differentiation. 
        

    :param step: the step 

    :param diff: differentiation (if -1, the expression will be a vector of size order with all orders) 

    :return: an expression"""
    ...

  def expr_t(
    self: Integrator,
    t: float, # double
    diff: int = -1, # int

  ) -> Expression:
    """Builds an expression for the given time and differentiation. 
        

    :param t: the time 

    :param diff: differentiation (if -1, the expression will be a vector of size order with all orders) 

    :return: an expression"""
    ...

  final_transition_matrix: numpy.ndarray # Eigen::MatrixXd
  """Caching the discrete matrix for the last step. 
        """

  def get_trajectory(
    self: Integrator,

  ) -> IntegratorTrajectory:
    """Retrieve a trajectory after a solve. 
        

    :return: trajectory"""
    ...

  t_start: float # double
  """Time offset for the trajectory. 
        """

  @staticmethod
  def upper_shift_matrix(
    order: int, # int

  ) -> numpy.ndarray:
    """Builds a matrix M so that the system differential equation is dX = M X. 
        

    :return: the matrix M"""
    ...

  def value(
    self: Integrator,
    t: float, # double
    diff: int, # int

  ) -> float:
    """Computes. 
        

    :param t: 

    :param diff: 

    :return:"""
    ...


class IntegratorTrajectory:
  """The trajectory can be detached after a solve to retrieve the continuous trajectory produced by the solver. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def duration(
    self: IntegratorTrajectory,

  ) -> float:
    """Trajectory duration. 
        

    :return: duration"""
    ...

  def value(
    self: IntegratorTrajectory,
    t: float, # double
    diff: int, # int

  ) -> float:
    """Gets the value of the trajectory at a given time and differentiation. 
        

    :param t: time 

    :param diff: differentiation 

    :return: the value"""
    ...


class JointsTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    self: JointsTask,

  ) -> any:
    """see KinematicsSolver::add_joints_task"""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: JointsTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: JointsTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: JointsTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def set_joint(
    self: JointsTask,
    joint: str, # std::string
    target: float, # double

  ) -> None:
    """Sets a joint target. 
        

    :param joint: joint 

    :param target: target value"""
    ...

  def set_joints(
    arg1: JointsTask,
    arg2: dict,

  ) -> None:
    ...

  def update(
    self: JointsTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class KinematicsConstraint:
  def __init__(

  ) -> any:
    ...

  def configure(
    self: KinematicsConstraint,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """


class KinematicsSolver:
  """Inverse Kinematics solver. 
    """
  N: int # int
  """Size of the problem (number of variables) 
        """

  def __init__(
    self: KinematicsSolver,
    robot_: RobotWrapper, # placo::model::RobotWrapper

  ) -> any:
    ...

  def add_avoid_self_collisions_constraint(
    self: KinematicsSolver,

  ) -> AvoidSelfCollisionsKinematicsConstraint:
    """Adds a self collision avoidance constraint. 
        

    :return: constraint"""
    ...

  def add_axisalign_task(
    self: KinematicsSolver,
    frame: str, # std::string
    axis_frame: numpy.ndarray, # Eigen::Vector3d
    targetAxis_world: numpy.ndarray, # Eigen::Vector3d

  ) -> AxisAlignTask:
    """Adds an axis alignment task. The goal here is to keep the given axis (expressed in the given frame) aligned with another one (given in the world) 
        

    :param frame: the robot frame we want to control 

    :param axis_frame: the axis to align, expressed in the robot frame 

    :param targetAxis_world: the target axis (in the world) we want to be aligned with"""
    ...

  def add_centroidal_momentum_task(
    self: KinematicsSolver,
    L_world: numpy.ndarray, # Eigen::Vector3d

  ) -> CentroidalMomentumTask:
    """Adding a centroidal momentum task. 
        

    :param L_world: desired centroidal angular momentum in the world 

    :return: centroidal task"""
    ...

  def add_com_polygon_constraint(
    self: KinematicsSolver,
    polygon: list[numpy.ndarray], # std::vector< Eigen::Vector2d >
    margin: float = 0., # double

  ) -> CoMPolygonConstraint:
    """Adds a CoM polygon constraint. 
        

    :param polygon: clockwise polygon 

    :param margin: margin 

    :return: constraint"""
    ...

  def add_com_task(
    self: KinematicsSolver,
    targetCom_world: numpy.ndarray, # Eigen::Vector3d

  ) -> CoMTask:
    """Adds a com position task. 
        

    :param targetCom_world: the target position, expressed in the world (as T_world_frame) 

    :return: com task"""
    ...

  def add_cone_constraint(
    self: KinematicsSolver,
    frame_a: str, # std::string
    frame_b: str, # std::string
    alpha_max: float, # double

  ) -> ConeConstraint:
    """Adds a Cone constraint. 
        

    :param frame_a: frame A 

    :param frame_b: frame B 

    :param alpha_max: alpha max (in radians) between the frame z-axis and the cone frame zt-axis 

    :param T_world_cone: cone frame 

    :return: constraint"""
    ...

  def add_constraint(
    self: KinematicsSolver,
    constraint: any, # T *

  ) -> any:
    ...

  def add_distance_task(
    self: KinematicsSolver,
    frame_a: str, # std::string
    frame_b: str, # std::string
    distance: float, # double

  ) -> DistanceTask:
    """Adds a distance task to be maintained between two frames. 
        

    :param frame_a: frame a 

    :param frame_b: frame b 

    :param distance: distance to maintain 

    :return: distance task"""
    ...

  def add_frame_task(
    self: KinematicsSolver,
    frame: str, # std::string
    T_world_frame: numpy.ndarray, # Eigen::Affine3d

  ) -> FrameTask:
    """Adds a frame task, this is equivalent to a position + orientation task, resulting in decoupled tasks for a given frame. 
        

    :param frame: the robot frame we want to control 

    :param T_world_frame: the target for the frame we want to control, expressed in the world (as T_world_frame) 

    :param priority: task priority (hard: equality constraint, soft: objective function) 

    :return: frame task"""
    ...

  def add_gear_task(
    self: KinematicsSolver,

  ) -> GearTask:
    """Adds a gear task, allowing replication of joints. 
        

    :return: gear task"""
    ...

  def add_joints_task(
    self: KinematicsSolver,

  ) -> JointsTask:
    """Adds joints task. 
        

    :return: joints task"""
    ...

  def add_kinetic_energy_regularization_task(
    self: KinematicsSolver,
    magnitude: float = 1e-6, # double

  ) -> KineticEnergyRegularizationTask:
    """Adds a kinetic energy regularization task for a given magnitude. 
        

    :param magnitude: regularization magnitude 

    :return: regularization task"""
    ...

  def add_orientation_task(
    self: KinematicsSolver,
    frame: str, # std::string
    R_world_frame: numpy.ndarray, # Eigen::Matrix3d

  ) -> OrientationTask:
    """Adds an orientation task. 
        

    :param frame: the robot frame we want to control 

    :param R_world_frame: the target orientation we want to achieve, expressed in the world (as T_world_frame) 

    :return: orientation task"""
    ...

  def add_position_task(
    self: KinematicsSolver,
    frame: str, # std::string
    target_world: numpy.ndarray, # Eigen::Vector3d

  ) -> PositionTask:
    """Adds a position task. 
        

    :param frame: the robot frame we want to control 

    :param target_world: the target position, expressed in the world (as T_world_frame) 

    :return: position task"""
    ...

  def add_regularization_task(
    self: KinematicsSolver,
    magnitude: float = 1e-6, # double

  ) -> RegularizationTask:
    """Adds a regularization task for a given magnitude. 
        

    :param magnitude: regularization magnitude 

    :return: regularization task"""
    ...

  def add_relative_frame_task(
    self: KinematicsSolver,
    frame_a: str, # std::string
    frame_b: str, # std::string
    T_a_b: numpy.ndarray, # Eigen::Affine3d

  ) -> RelativeFrameTask:
    """Adds a relative frame task. 
        

    :param frame_a: frame a 

    :param frame_b: frame b 

    :param T_a_b: desired transformation 

    :return: relative frame task"""
    ...

  def add_relative_orientation_task(
    self: KinematicsSolver,
    frame_a: str, # std::string
    frame_b: str, # std::string
    R_a_b: numpy.ndarray, # Eigen::Matrix3d

  ) -> RelativeOrientationTask:
    """Adds a relative orientation task. 
        

    :param frame_a: frame a 

    :param frame_b: frame b 

    :param R_a_b: the desired orientation 

    :return: relative orientation task"""
    ...

  def add_relative_position_task(
    self: KinematicsSolver,
    frame_a: str, # std::string
    frame_b: str, # std::string
    target: numpy.ndarray, # Eigen::Vector3d

  ) -> RelativePositionTask:
    """Adds a relative position task. 
        

    :param frame_a: frame a 

    :param frame_b: frame b 

    :param target: the target vector between frame a and b (expressed in world) 

    :return: relative position task"""
    ...

  def add_task(
    self: KinematicsSolver,
    task: any, # T *

  ) -> any:
    ...

  def add_wheel_task(
    self: KinematicsSolver,
    joint: str, # const std::string
    radius: float, # double
    omniwheel: bool = False, # bool

  ) -> WheelTask:
    """Adds a wheel task. 
        

    :param joint: joint name 

    :param radius: wheel radius 

    :param omniwheel: true if it's an omniwheel (can slide laterally) 

    :return: the wheel task"""
    ...

  def clear(
    self: KinematicsSolver,

  ) -> None:
    """Clears the internal tasks."""
    ...

  dt: float # double
  """solver dt (for speeds limiting) 
        """

  def dump_status(
    self: KinematicsSolver,

  ) -> None:
    """Shows the tasks status."""
    ...

  def enable_joint_limits(
    self: KinematicsSolver,
    enable: bool, # bool

  ) -> None:
    """Enables/disables joint limits inequalities."""
    ...

  def enable_velocity_limits(
    self: KinematicsSolver,
    enable: bool, # bool

  ) -> None:
    """Enables/disables joint velocity inequalities."""
    ...

  def mask_dof(
    self: KinematicsSolver,
    dof: str, # std::string

  ) -> None:
    """Masks (disables a DoF) from being used by the QP solver (it can't provide speed) 
        

    :param dof: the dof name"""
    ...

  def mask_fbase(
    self: KinematicsSolver,
    masked: bool, # bool

  ) -> None:
    """Decides if the floating base should be masked."""
    ...

  noise: float # double
  """Some configuration noise added before solving. 
        """

  problem: Problem # placo::problem::Problem
  """The underlying QP problem. 
        """

  def remove_constraint(
    self: KinematicsSolver,
    constraint: KinematicsConstraint, # placo::kinematics::Constraint

  ) -> None:
    """Removes aconstraint from the solver. 
        

    :param constraint: constraint"""
    ...

  def remove_task(
    self: KinematicsSolver,
    task: FrameTask, # placo::kinematics::FrameTask

  ) -> None:
    """Removes a frame task from the solver. 
        

    :param task: task"""
    ...

  robot: RobotWrapper # placo::model::RobotWrapper
  """The robot controlled by this solver. 
        """

  scale: float # double
  """scale obtained when using tasks scaling 
        """

  def solve(
    self: KinematicsSolver,
    apply: bool = False, # bool

  ) -> numpy.ndarray:
    """Constructs the QP problem and solves it. 
        

    :param apply: apply the solution to the robot model 

    :return: the vector containing delta q, which are target variations for the robot degrees of freedom."""
    ...

  def tasks_count(
    self: KinematicsSolver,

  ) -> int:
    """Number of tasks."""
    ...

  def unmask_dof(
    self: KinematicsSolver,
    dof: str, # std::string

  ) -> None:
    """Unmsks (enables a DoF) from being used by the QP solver (it can provide speed) 
        

    :param dof: the dof name"""
    ...


class KineticEnergyRegularizationTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    arg1: object,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: KineticEnergyRegularizationTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: KineticEnergyRegularizationTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: KineticEnergyRegularizationTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def update(
    self: KineticEnergyRegularizationTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class LIPM:
  """LIPM is an helper that can be used to build problem involving LIPM dynamics. The decision variables introduced here are jerks, which is piecewise constant. 
    """
  def __init__(
    self: LIPM,
    problem: Problem, # placo::problem::Problem
    timesteps: int, # int
    dt: float, # double
    initial_pos: numpy.ndarray, # Eigen::Vector2d
    initial_vel: numpy.ndarray, # Eigen::Vector2d
    initial_acc: numpy.ndarray, # Eigen::Vector2d

  ) -> any:
    ...

  def acc(
    self: LIPM,
    timestep: int, # int

  ) -> Expression:
    ...

  @staticmethod
  def compute_omega(
    com_height: float, # double

  ) -> float:
    """Compute the natural frequency of a LIPM given its height (omega = sqrt(g / h))"""
    ...

  def dcm(
    self: LIPM,
    timestep: int, # int
    omega: float, # double

  ) -> Expression:
    ...

  def dzmp(
    self: LIPM,
    timestep: int, # int
    omega_2: float, # double

  ) -> Expression:
    ...

  def get_trajectory(
    self: LIPM,

  ) -> LIPMTrajectory:
    ...

  def jerk(
    self: LIPM,
    timestep: int, # int

  ) -> Expression:
    ...

  def pos(
    self: LIPM,
    timestep: int, # int

  ) -> Expression:
    ...

  def vel(
    self: LIPM,
    timestep: int, # int

  ) -> Expression:
    ...

  x: Integrator # placo::problem::Integrator

  y: Integrator # placo::problem::Integrator

  def zmp(
    self: LIPM,
    timestep: int, # int
    omega_2: float, # double

  ) -> Expression:
    ...


class LIPMTrajectory:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def acc(
    self: LIPMTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def dcm(
    self: LIPMTrajectory,
    t: float, # double
    omega: float, # double

  ) -> numpy.ndarray:
    ...

  def dzmp(
    self: LIPMTrajectory,
    t: float, # double
    omega_2: float, # double

  ) -> numpy.ndarray:
    ...

  def jerk(
    self: LIPMTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def pos(
    self: LIPMTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def vel(
    self: LIPMTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def zmp(
    self: LIPMTrajectory,
    t: float, # double
    omega_2: float, # double

  ) -> numpy.ndarray:
    ...


class OrientationTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  R_world_frame: numpy.ndarray # Eigen::Matrix3d
  """Target frame orientation in the world. 
        """

  def __init__(
    self: OrientationTask,
    frame_index: any, # pinocchio::FrameIndex
    R_world_frame: numpy.ndarray, # Eigen::Matrix3d

  ) -> any:
    """See KinematicsSolver::add_orientation_task."""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: OrientationTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: OrientationTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: OrientationTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  frame_index: any # pinocchio::FrameIndex
  """Frame. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def update(
    self: OrientationTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class PointContact:
  def __init__(
    self: PointContact,
    position_task: DynamicsPositionTask, # placo::dynamics::PositionTask
    unilateral: bool, # bool

  ) -> any:
    """see DynamicsSolver::add_point_contact and DynamicsSolver::add_unilateral_point_contact"""
    ...

  active: bool # bool
  """true if the contact is active (ignored by the solver else, this allow to enable/disable a contact without removing it from the solver) 
        """

  mu: float # double
  """Coefficient of friction (if relevant) 
        """

  def position_task(
    self: PointContact,

  ) -> DynamicsPositionTask:
    """associated position task"""
    ...

  unilateral: bool # bool
  """true for unilateral contact with the ground 
        """

  weight_forces: float # double
  """Weight of forces for the optimization (if relevant) 
        """

  weight_moments: float # double
  """Weight of moments for optimization (if relevant) 
        """

  wrench: numpy.ndarray # Eigen::VectorXd
  """Wrench populated after the DynamicsSolver::solve call. 
        """


class PolygonConstraint:
  """Provides convenient helpers to build 2D polygon belonging constraints. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  @staticmethod
  def in_polygon(
    expression_x: Expression, # placo::problem::Expression
    expression_y: Expression, # placo::problem::Expression
    polygon: list[numpy.ndarray], # std::vector< Eigen::Vector2d >
    margin: float = 0., # double

  ) -> ProblemConstraint:
    ...

  @staticmethod
  def in_polygon_xy(
    expression_xy: Expression, # placo::problem::Expression
    polygon: list[numpy.ndarray], # std::vector< Eigen::Vector2d >
    margin: float = 0., # double

  ) -> ProblemConstraint:
    """Given a polygon, produces inequalities so that the given point lies inside the polygon. WARNING: Polygon must be clockwise (meaning that the exterior of the shape is on the trigonometric normal of the vertices)"""
    ...


class PositionTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    self: PositionTask,
    frame_index: any, # pinocchio::FrameIndex
    target_world: numpy.ndarray, # Eigen::Vector3d

  ) -> any:
    """See KinematicsSolver::add_position_task."""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: PositionTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: PositionTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: PositionTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  frame_index: any # pinocchio::FrameIndex
  """Frame. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  target_world: numpy.ndarray # Eigen::Vector3d
  """Target position in the world. 
        """

  def update(
    self: PositionTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class Prioritized:
  """Represents an object (like a task or a constraint) that is prioritized. 
    """
  def __init__(
    self: Prioritized,

  ) -> any:
    ...

  def configure(
    self: Prioritized,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """


class Problem:
  """A problem is an object that has variables and constraints to be solved by a QP solver. 
    """
  def __init__(
    self: Problem,

  ) -> any:
    ...

  def add_constraint(
    self: Problem,
    constraint: ProblemConstraint, # placo::problem::ProblemConstraint

  ) -> ProblemConstraint:
    """Adds a given constraint to the problem. 
        

    :param constraint: 

    :return: The constraint"""
    ...

  def add_limit(
    self: Problem,
    expression: Expression, # placo::problem::Expression
    target: numpy.ndarray, # Eigen::VectorXd

  ) -> ProblemConstraint:
    """Adds a limit, "absolute" inequality constraint (abs(Ax + b) <= t) 
        

    :param expression: 

    :param target: 

    :return: The constraint"""
    ...

  def add_variable(
    self: Problem,
    size: int = 1, # int

  ) -> Variable:
    """Adds a n-dimensional variable to a problem. 
        

    :param size: dimension of the variable 

    :return: variable"""
    ...

  def clear_constraints(
    self: Problem,

  ) -> None:
    """Clear all the constraints."""
    ...

  def clear_variables(
    self: Problem,

  ) -> None:
    """Clear all the variables."""
    ...

  determined_variables: int # int
  """Number of determined variables. 
        """

  def dump_status(
    self: Problem,

  ) -> None:
    ...

  free_variables: int # int
  """Number of free variables to solve. 
        """

  n_equalities: int # int
  """Number of equalities. 
        """

  n_inequalities: int # int
  """Number of inequality constraints. 
        """

  n_variables: int # int
  """Number of problem variables that need to be solved. 
        """

  rewrite_equalities: bool # bool
  """If set to true, a QR factorization will be performed on the equality constraints, and the QP will be called with free variables only. 
        """

  slack_variables: int # int
  """Number of slack variables in the solver. 
        """

  slacks: numpy.ndarray # Eigen::VectorXd
  """Computed slack variables. 
        """

  def solve(
    self: Problem,

  ) -> None:
    """Solves the problem, raises QPError in case of failure."""
    ...

  use_sparsity: bool # bool
  """If set to true, some sparsity optimizations will be performed when building the problem Hessian. This optimization is generally not useful for small problems. 
        """


class ProblemConstraint:
  """Represents a constraint to be enforced by a Problem. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def configure(
    self: ProblemConstraint,
    type: str, # std::string
    weight: float = 1.0, # double

  ) -> None:
    """Configures the constraint. 
        

    :param priority: priority 

    :param weight: weight"""
    ...

  expression: Expression # placo::problem::Expression
  """The constraint expression (Ax + b) 
        """

  is_active: bool # bool
  """This flag will be set by the solver if the constraint is active in the optimal solution. 
        """

  priority: any # placo::problem::ProblemConstraint::Priority
  """Constraint priority. 
        """

  weight: float # double
  """Constraint weight (for soft constraints) 
        """


class PuppetContact:
  def __init__(
    self: PuppetContact,

  ) -> any:
    """see DynamicsSolver::add_puppet_contact"""
    ...

  active: bool # bool
  """true if the contact is active (ignored by the solver else, this allow to enable/disable a contact without removing it from the solver) 
        """

  mu: float # double
  """Coefficient of friction (if relevant) 
        """

  weight_forces: float # double
  """Weight of forces for the optimization (if relevant) 
        """

  weight_moments: float # double
  """Weight of moments for optimization (if relevant) 
        """

  wrench: numpy.ndarray # Eigen::VectorXd
  """Wrench populated after the DynamicsSolver::solve call. 
        """


class QPError:
  """Exception raised by Problem in case of failure. 
    """
  def __init__(
    self: QPError,
    message: str = "", # std::string

  ) -> any:
    ...

  def what(
    arg1: QPError,

  ) -> str:
    ...


class RegularizationTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    arg1: object,

  ) -> None:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: RegularizationTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: RegularizationTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: RegularizationTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def update(
    self: RegularizationTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class Relative6DContact:
  def __init__(
    self: Relative6DContact,
    frame_task: DynamicsRelativeFrameTask, # placo::dynamics::RelativeFrameTask

  ) -> any:
    """see DynamicsSolver::add_relative_fixed_contact"""
    ...

  active: bool # bool
  """true if the contact is active (ignored by the solver else, this allow to enable/disable a contact without removing it from the solver) 
        """

  mu: float # double
  """Coefficient of friction (if relevant) 
        """

  weight_forces: float # double
  """Weight of forces for the optimization (if relevant) 
        """

  weight_moments: float # double
  """Weight of moments for optimization (if relevant) 
        """

  wrench: numpy.ndarray # Eigen::VectorXd
  """Wrench populated after the DynamicsSolver::solve call. 
        """


class RelativeFrameTask:
  T_a_b: any

  def __init__(
    self: RelativeFrameTask,
    position: RelativePositionTask, # placo::kinematics::RelativePositionTask
    orientation: RelativeOrientationTask, # placo::kinematics::RelativeOrientationTask

  ) -> any:
    """see KinematicsSolver::add_relative_frame_task"""
    ...

  def configure(
    self: RelativeFrameTask,
    name: str, # std::string
    priority: str = "soft", # std::string
    position_weight: float = 1.0, # double
    orientation_weight: float = 1.0, # double

  ) -> None:
    """Configures the relative frame task. 
        

    :param name: task name 

    :param priority: task priority 

    :param position_weight: weight for the position task 

    :param orientation_weight: weight for the orientation task"""
    ...

  def orientation(
    self: RelativeFrameTask,

  ) -> RelativeOrientationTask:
    """Relative orientation."""
    ...

  def position(
    self: RelativeFrameTask,

  ) -> RelativePositionTask:
    """Relative position."""
    ...


class RelativeOrientationTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  R_a_b: numpy.ndarray # Eigen::Matrix3d
  """Target relative orientation of b in a. 
        """

  def __init__(
    self: RelativeOrientationTask,
    frame_a: any, # pinocchio::FrameIndex
    frame_b: any, # pinocchio::FrameIndex
    R_a_b: numpy.ndarray, # Eigen::Matrix3d

  ) -> any:
    """See KinematicsSolver::add_relative_orientation_task."""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: RelativeOrientationTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: RelativeOrientationTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: RelativeOrientationTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  frame_a: any # pinocchio::FrameIndex
  """Frame A. 
        """

  frame_b: any # pinocchio::FrameIndex
  """Frame B. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def update(
    self: RelativeOrientationTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class RelativePointContact:
  def __init__(
    self: RelativePointContact,
    position_task: DynamicsRelativePositionTask, # placo::dynamics::RelativePositionTask

  ) -> any:
    """see DynamicsSolver::add_relative_point_contact"""
    ...

  active: bool # bool
  """true if the contact is active (ignored by the solver else, this allow to enable/disable a contact without removing it from the solver) 
        """

  mu: float # double
  """Coefficient of friction (if relevant) 
        """

  weight_forces: float # double
  """Weight of forces for the optimization (if relevant) 
        """

  weight_moments: float # double
  """Weight of moments for optimization (if relevant) 
        """

  wrench: numpy.ndarray # Eigen::VectorXd
  """Wrench populated after the DynamicsSolver::solve call. 
        """


class RelativePositionTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(
    self: RelativePositionTask,
    frame_a: any, # pinocchio::FrameIndex
    frame_b: any, # pinocchio::FrameIndex
    target: numpy.ndarray, # Eigen::Vector3d

  ) -> any:
    """See KinematicsSolver::add_relative_position_task."""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: RelativePositionTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: RelativePositionTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: RelativePositionTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  frame_a: any # pinocchio::FrameIndex
  """Frame A. 
        """

  frame_b: any # pinocchio::FrameIndex
  """Frame B. 
        """

  mask: AxisesMask # placo::tools::AxisesMask
  """Mask. 
        """

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  target: numpy.ndarray # Eigen::Vector3d
  """Target position of B in A. 
        """

  def update(
    self: RelativePositionTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class RobotWrapper:
  """This class contains the robot model, state, and all convenient methods. All the rigid body algorithms (namely, based on pinocchio) are wrapped in this object. 
    """
  def __init__(
    self: RobotWrapper,
    model_directory: str, # std::string
    flags: int = 0, # int
    urdf_content: str = "", # std::string

  ) -> any:
    """Creates a robot wrapper from a URDF file. 
        

    :param model_directory: robot model (URDF). It can be a path to an URDF file, or a directory containing an URDF file named 'robot.urdf' 

    :param flags: see Flags 

    :param urdf_content: if it is not empty, it will be used as the URDF content instead of loading it from the file"""
    ...

  collision_model: any # pinocchio::GeometryModel
  """Pinocchio collision model. 
        """

  def com_jacobian(
    self: RobotWrapper,

  ) -> any:
    """Jacobian of the CoM position expressed in the world. 
        

    :return: jacobian (3 x n matrix)"""
    ...

  def com_jacobian_time_variation(
    self: RobotWrapper,

  ) -> any:
    """Jacobian time variation of the CoM expressed in the world. 
        

    :return: jacobian (3 x n matrix)"""
    ...

  def com_world(
    self: RobotWrapper,

  ) -> numpy.ndarray:
    """Gets the CoM position in the world."""
    ...

  def distances(
    self: RobotWrapper,

  ) -> list[Distance]:
    """Computes all minimum distances between current collision pairs. 
        

    :return: vector of Distance"""
    ...

  def frame_jacobian(
    self: RobotWrapper,
    frame: str, # const std::string &
    reference: str = "local_world_aligned", # const std::string &

  ) -> numpy.ndarray:
    """Frame jacobian, default reference is LOCAL_WORLD_ALIGNED. 
        

    :param frame: the frame for which we want the jacobian 

    :return: jacobian (6 x nv matrix), where nv is the size of qd"""
    ...

  def frame_jacobian_time_variation(
    self: RobotWrapper,
    frame: str, # const std::string &
    reference: str = "local_world_" "aligned", # const std::string &

  ) -> numpy.ndarray:
    """Jacobian time variation $\dot J$, default reference is LOCAL_WORLD_ALIGNED. 
        

    :param frame: the frame for which we want the jacobian time variation 

    :param reference: the reference frame 

    :return: jacobian time variation (6 x nv matrix), where nv is the size of qd"""
    ...

  def frame_names(
    self: RobotWrapper,

  ) -> list[str]:
    """All the frame names."""
    ...

  def generalized_gravity(
    self: RobotWrapper,

  ) -> numpy.ndarray:
    """Computes generalized gravity."""
    ...

  def get_T_a_b(
    self: RobotWrapper,
    frame_a: str, # const std::string &
    frame_b: str, # const std::string &

  ) -> numpy.ndarray:
    """Gets the transformation matrix from frame b to a. 
        

    :param frame_a: frame a 

    :param frame_b: frame b 

    :return: transformation"""
    ...

  def get_T_world_fbase(
    self: RobotWrapper,

  ) -> numpy.ndarray:
    """Returns the transformation matrix from the fbase frame (which is the root of the URDF) to the world. 
        

    :return: transformation"""
    ...

  def get_T_world_frame(
    self: RobotWrapper,
    frame: str, # const std::string &

  ) -> numpy.ndarray:
    """Gets the frame to world transformation matrix for a given frame. 
        

    :param frame: frame 

    :return: transformation"""
    ...

  def get_joint(
    self: RobotWrapper,
    name: str, # const std::string &

  ) -> float:
    """Retrieves a joint value from state.q. 
        

    :param name: joint name 

    :return: the joint current (inner state) value (e.g rad for revolute or meters for prismatic)"""
    ...

  def get_joint_acceleration(
    self: RobotWrapper,
    name: str, # const std::string &

  ) -> float:
    """Gets the joint acceleration from state.qd. 
        

    :param name: joint name 

    :return: joint acceleration"""
    ...

  def get_joint_offset(
    self: RobotWrapper,
    name: str, # const std::string &

  ) -> int:
    """Gets the offset for a given joint in the state (in State::q) 
        

    :param name: joint name 

    :return: offset in state.q"""
    ...

  def get_joint_v_offset(
    self: RobotWrapper,
    name: str, # const std::string &

  ) -> int:
    """Gets the offset for a given joint in the state (in State::qd and State::qdd) 
        

    :param name: joint name 

    :return: offset in state.qd and state.qdd"""
    ...

  def get_joint_velocity(
    self: RobotWrapper,
    name: str, # const std::string &

  ) -> float:
    """Gets the joint velocity from state.qd. 
        

    :param name: joint name 

    :return: joint velocity"""
    ...

  def integrate(
    self: RobotWrapper,
    dt: float, # double

  ) -> None:
    """Integrates the internal state for a given dt 
        

    :param dt: delta time for integration expressed in seconds"""
    ...

  def joint_jacobian(
    self: RobotWrapper,
    joint: str, # const std::string &
    reference: str = "local_world_aligned", # const std::string &

  ) -> numpy.ndarray:
    ...

  def joint_names(
    self: RobotWrapper,
    include_floating_base: bool = False, # bool

  ) -> list[str]:
    """All the joint names. 
        

    :param include_floating_base: whether to include the floating base joint (false by default)"""
    ...

  def load_collision_pairs(
    self: RobotWrapper,
    filename: str, # const std::string &

  ) -> None:
    """Loads collision pairs from a given JSON file. 
        

    :param filename: path to collisions.json file"""
    ...

  def make_solver(
    arg1: RobotWrapper,

  ) -> KinematicsSolver:
    ...

  def mass_matrix(
    self: RobotWrapper,

  ) -> numpy.ndarray:
    """Computes the mass matrix."""
    ...

  model: any # pinocchio::Model
  """Pinocchio model. 
        """

  def neutral_state(
    self: RobotWrapper,

  ) -> RobotWrapper_State:
    """builds a neutral state (neutral position, zero speed) 
        

    :return: the state"""
    ...

  def non_linear_effects(
    self: RobotWrapper,

  ) -> numpy.ndarray:
    """Computes non-linear effects (Corriolis, centrifual and gravitationnal effects)"""
    ...

  def relative_position_jacobian(
    self: RobotWrapper,
    frame_a: str, # const std::string &
    frame_b: str, # const std::string &

  ) -> numpy.ndarray:
    """Jacobian of the relative position of the position of b expressed in a. 
        

    :param frame_a: frame A 

    :param frame_b: frame B 

    :return: relative position jacobian of b expressed in a (3 x n matrix)"""
    ...

  def reset(
    self: RobotWrapper,

  ) -> None:
    """Reset internal states, this sets q to the neutral position, qd and qdd to zero."""
    ...

  def self_collisions(
    self: RobotWrapper,
    stop_at_first: bool = False, # bool

  ) -> list[Collision]:
    """Finds the self collision in current state, if stop_at_first is true, it will stop at the first collision found. 
        

    :param stop_at_first: whether to stop at the first collision found 

    :return: a vector of Collision"""
    ...

  def set_T_world_fbase(
    self: RobotWrapper,
    T_world_fbase: numpy.ndarray, # Eigen::Affine3d

  ) -> None:
    """Updates the floating base to match the given transformation matrix. 
        

    :param T_world_fbase: transformation matrix"""
    ...

  def set_T_world_frame(
    self: RobotWrapper,
    frame: str, # const std::string &
    T_world_frameTarget: numpy.ndarray, # Eigen::Affine3d

  ) -> None:
    """Updates the floating base status so that the given frame has the given transformation matrix. 
        

    :param frame: frame to update 

    :param T_world_frameTarget: transformation matrix"""
    ...

  def set_gravity(
    self: RobotWrapper,
    gravity: numpy.ndarray, # Eigen::Vector3d

  ) -> None:
    """Sets the gravity vector."""
    ...

  def set_joint(
    self: RobotWrapper,
    name: str, # const std::string &
    value: float, # double

  ) -> None:
    """Sets the value of a joint in state.q. 
        

    :param name: joint name 

    :param value: joint value (e.g rad for revolute or meters for prismatic)"""
    ...

  def set_joint_acceleration(
    self: RobotWrapper,
    name: str, # const std::string &
    value: float, # double

  ) -> None:
    """Sets the joint acceleration in state.qd. 
        

    :param name: joint name 

    :param value: joint acceleration"""
    ...

  def set_joint_limits(
    self: RobotWrapper,
    name: str, # const std::string &
    lower: float, # double
    upper: float, # double

  ) -> None:
    """Sets the limits for a given joint. 
        

    :param name: joint name 

    :param lower: lower limit 

    :param upper: upper limit"""
    ...

  def set_joint_velocity(
    self: RobotWrapper,
    name: str, # const std::string &
    value: float, # double

  ) -> None:
    """Sets the joint velocity in state.qd. 
        

    :param name: joint name 

    :param value: joint velocity"""
    ...

  def set_torque_limit(
    self: RobotWrapper,
    name: str, # const std::string &
    limit: float, # double

  ) -> None:
    """Sets the torque limit for a given joint. 
        

    :param name: joint name 

    :param limit: torque limit"""
    ...

  def set_velocity_limit(
    self: RobotWrapper,
    name: str, # const std::string &
    limit: float, # double

  ) -> None:
    """Sets the velocity limit for a given joint. 
        

    :param name: joint name 

    :param limit: joint limit"""
    ...

  def set_velocity_limits(
    self: RobotWrapper,
    limit: float, # double

  ) -> None:
    """Set the velocity limits for all the joints. 
        

    :param limit: limit"""
    ...

  state: RobotWrapper_State # placo::model::RobotWrapper::State
  """Robot's current state. 
        """

  def static_gravity_compensation_torques(
    self: RobotWrapper,
    frame: str, # std::string

  ) -> numpy.ndarray:
    """Computes torques needed by the robot to compensate for the generalized gravity, assuming that the given frame is the (only) contact supporting the robot. 
        

    :param frame: frame"""
    ...

  def static_gravity_compensation_torques_dict(
    arg1: RobotWrapper,
    arg2: str,

  ) -> dict:
    ...

  def torques_from_acceleration_with_fixed_frame(
    self: RobotWrapper,
    qdd_a: numpy.ndarray, # Eigen::VectorXd
    fixed_frame: str, # std::string

  ) -> numpy.ndarray:
    """Computes required torques in the robot DOFs for a given acceleration of the actuated DOFs, assuming that the given frame is fixed. 
        

    :param qdd_a: acceleration of the actuated DOFs 

    :param fixed_frame: frame"""
    ...

  def torques_from_acceleration_with_fixed_frame_dict(
    arg1: RobotWrapper,
    arg2: numpy.ndarray,
    arg3: str,

  ) -> dict:
    ...

  def total_mass(
    self: RobotWrapper,

  ) -> float:
    """Total mass."""
    ...

  def update_kinematics(
    self: RobotWrapper,

  ) -> None:
    """Update internal computation for kinematics (frames, jacobian). This method should be called when the robot state has changed."""
    ...

  visual_model: any # pinocchio::GeometryModel
  """Pinocchio visual model. 
        """


class RobotWrapper_State:
  """Represents the robot state. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  q: numpy.ndarray # Eigen::VectorXd
  """joints configuration $q$ 
        """

  qd: numpy.ndarray # Eigen::VectorXd
  """joints velocity $\dot q$ 
        """

  qdd: numpy.ndarray # Eigen::VectorXd
  """joints acceleration $\ddot q$ 
        """


class Sparsity:
  """Internal helper to check the column sparsity of a matrix. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def add_interval(
    self: Sparsity,
    start: int, # int
    end: int, # int

  ) -> None:
    """Adds an interval to the sparsity, this will compute the union of intervals. 
        

    :param start: interval start 

    :param end: interval end"""
    ...

  @staticmethod
  def detect_columns_sparsity(
    M: numpy.ndarray, # const Eigen::MatrixXd

  ) -> Sparsity:
    """Helper to detect columns sparsity. 
        

    :param M: given matrix 

    :return: sparsity"""
    ...

  intervals: list[SparsityInterval] # std::vector<placo::problem::Sparsity::Interval>
  """Intervals of non-sparse columns. 
        """

  def print_intervals(
    self: Sparsity,

  ) -> None:
    """Print intervals."""
    ...


class SparsityInterval:
  """An interval is a range of columns that are not sparse. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  end: int # int
  """End of interval. 
        """

  start: int # int
  """Start of interval. 
        """


class Support:
  """A support is a set of footsteps (can be one or two foot on the ground) 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  end: bool # bool

  def footstep_frame(
    self: Support,
    side: any, # placo::humanoid::HumanoidRobot::Side

  ) -> numpy.ndarray:
    """Returns the frame for a given side (if present) 
        

    :param side: the side we want the frame (left or right foot) 

    :return: a frame"""
    ...

  footsteps: list[Footstep] # std::vector<placo::humanoid::FootstepsPlanner::Footstep>

  def frame(
    self: Support,

  ) -> numpy.ndarray:
    """Returns the frame for the support. It will be the (interpolated) average of footsteps frames. 
        

    :return: a frame"""
    ...

  def is_both(
    self: Support,

  ) -> bool:
    """Checks whether this support is a double support."""
    ...

  def kick(
    self: Support,

  ) -> bool:
    ...

  def set_end(
    arg1: Support,
    arg2: bool,

  ) -> None:
    ...

  def set_start(
    arg1: Support,
    arg2: bool,

  ) -> None:
    ...

  def side(
    self: Support,

  ) -> any:
    """The support side (you should call is_both() to be sure it's not a double support before)"""
    ...

  start: bool # bool

  def support_polygon(
    self: Support,

  ) -> list[numpy.ndarray]:
    ...


class Supports:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: Supports,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: Supports,
    arg2: object,

  ) -> None:
    ...


class SwingFoot:
  """A cubic fitting of swing foot, see: https://scaron.info/doc/pymanoid/walking-pattern-generation.html#pymanoid.swing_foot.SwingFoot. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  @staticmethod
  def make_trajectory(
    t_start: float, # double
    t_end: float, # double
    height: float, # double
    start: numpy.ndarray, # Eigen::Vector3d
    target: numpy.ndarray, # Eigen::Vector3d

  ) -> SwingFootTrajectory:
    ...

  @staticmethod
  def remake_trajectory(
    old_trajectory: SwingFootTrajectory, # placo::humanoid::SwingFoot::Trajectory
    t: float, # double
    target: numpy.ndarray, # Eigen::Vector3d

  ) -> SwingFootTrajectory:
    ...


class SwingFootCubic:
  """Cubic swing foot. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  @staticmethod
  def make_trajectory(
    t_start: float, # double
    t_end: float, # double
    height: float, # double
    rise_ratio: float, # double
    start: numpy.ndarray, # Eigen::Vector3d
    target: numpy.ndarray, # Eigen::Vector3d

  ) -> SwingFootCubicTrajectory:
    ...


class SwingFootCubicTrajectory:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def pos(
    self: SwingFootCubicTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def vel(
    self: SwingFootCubicTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...


class SwingFootQuintic:
  """A quintic fitting of the swing foot. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  @staticmethod
  def make_trajectory(
    t_start: float, # double
    t_end: float, # double
    height: float, # double
    start: numpy.ndarray, # Eigen::Vector3d
    target: numpy.ndarray, # Eigen::Vector3d

  ) -> SwingFootQuinticTrajectory:
    ...


class SwingFootQuinticTrajectory:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def pos(
    self: SwingFootQuinticTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def vel(
    self: SwingFootQuinticTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...


class SwingFootTrajectory:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def pos(
    self: SwingFootTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def vel(
    self: SwingFootTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...


class Task:
  """Represents a task for the kinematics solver. 
    """
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  def __init__(

  ) -> any:
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: Task,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: Task,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: Task,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  name: str # std::string
  """Object name. 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  def update(
    self: Task,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


class TaskContact:
  def __init__(
    self: TaskContact,
    task: DynamicsTask, # placo::dynamics::Task

  ) -> any:
    """see DynamicsSolver::add_task_contact"""
    ...

  active: bool # bool
  """true if the contact is active (ignored by the solver else, this allow to enable/disable a contact without removing it from the solver) 
        """

  mu: float # double
  """Coefficient of friction (if relevant) 
        """

  weight_forces: float # double
  """Weight of forces for the optimization (if relevant) 
        """

  weight_moments: float # double
  """Weight of moments for optimization (if relevant) 
        """

  wrench: numpy.ndarray # Eigen::VectorXd
  """Wrench populated after the DynamicsSolver::solve call. 
        """


class Variable:
  """Represents a variable in a Problem. 
    """
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def expr(
    self: Variable,
    start: int = -1, # int
    rows: int = -1, # int

  ) -> Expression:
    """Builds an expression from a variable. 
        

    :param start: start row (default: 0) 

    :param rows: number of rows (default: -1, all rows) 

    :return: expression"""
    ...

  k_end: int # int
  """End offset in the Problem. 
        """

  k_start: int # int
  """Start offset in the Problem. 
        """

  value: numpy.ndarray # Eigen::VectorXd
  """Variable value, populated by Problem after a solve. 
        """


class WalkPatternGenerator:
  def __init__(
    self: WalkPatternGenerator,
    robot: HumanoidRobot, # placo::humanoid::HumanoidRobot
    parameters: HumanoidParameters, # placo::humanoid::HumanoidParameters

  ) -> any:
    ...

  def can_replan_supports(
    self: WalkPatternGenerator,
    trajectory: WalkTrajectory, # placo::humanoid::WalkPatternGenerator::Trajectory
    t_replan: float, # double

  ) -> bool:
    """Checks if a trajectory can be replanned for supports."""
    ...

  def plan(
    self: WalkPatternGenerator,
    supports: list[Support], # std::vector<placo::humanoid::FootstepsPlanner::Support>
    initial_com_world: numpy.ndarray, # Eigen::Vector3d
    t_start: float = 0., # double

  ) -> WalkTrajectory:
    """Plan a walk trajectory following given footsteps based on the parameters of the WPG. 
        

    :param supports: Supports generated from the foosteps to follow 

    :return: Planned trajectory"""
    ...

  def replan(
    self: WalkPatternGenerator,
    supports: list[Support], # std::vector<placo::humanoid::FootstepsPlanner::Support>
    old_trajectory: WalkTrajectory, # placo::humanoid::WalkPatternGenerator::Trajectory
    t_replan: float, # double

  ) -> WalkTrajectory:
    """Update the walk trajectory to follow given footsteps based on the parameters of the WPG. 
        

    :param supports: Supports generated from the current foosteps or the new ones to follow. Contain the current support 

    :param old_trajectory: Current walk trajectory 

    :param t_replan: The time (in the original trajectory) where the replan happens 

    :return: True if the trajectory have been replanned, false it hasn't"""
    ...

  def replan_supports(
    self: WalkPatternGenerator,
    planner: FootstepsPlanner, # placo::humanoid::FootstepsPlanner
    trajectory: WalkTrajectory, # placo::humanoid::WalkPatternGenerator::Trajectory
    t_replan: float, # double

  ) -> list[Support]:
    """Replan the supports for a given trajectory given a footsteps planner."""
    ...


class WalkTasks:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  com_x: float # double

  com_y: float # double

  def get_tasks_error(
    self: WalkTasks,

  ) -> any:
    ...

  def initialize_tasks(
    self: WalkTasks,
    solver: KinematicsSolver, # placo::kinematics::KinematicsSolver
    robot: HumanoidRobot, # placo::humanoid::HumanoidRobot

  ) -> None:
    ...

  left_foot_task: FrameTask # placo::kinematics::FrameTask

  def reach_initial_pose(
    self: WalkTasks,
    T_world_left: numpy.ndarray, # Eigen::Affine3d
    feet_spacing: float, # double
    com_height: float, # double
    trunk_pitch: float, # double

  ) -> None:
    ...

  def remove_tasks(
    self: WalkTasks,

  ) -> None:
    ...

  right_foot_task: FrameTask # placo::kinematics::FrameTask

  scaled: bool # bool

  solver: KinematicsSolver # placo::kinematics::KinematicsSolver

  trunk_mode: bool # bool

  trunk_orientation_task: OrientationTask # placo::kinematics::OrientationTask

  def update_tasks(
    self: WalkTasks,
    T_world_left: numpy.ndarray, # Eigen::Affine3d
    T_world_right: numpy.ndarray, # Eigen::Affine3d
    com_world: numpy.ndarray, # Eigen::Vector3d
    R_world_trunk: numpy.ndarray, # Eigen::Matrix3d

  ) -> None:
    ...

  def update_tasks_from_trajectory(
    arg1: WalkTasks,
    arg2: WalkTrajectory,
    arg3: float,

  ) -> None:
    ...


class WalkTrajectory:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def apply_transform(
    self: WalkTrajectory,
    T: numpy.ndarray, # Eigen::Affine3d

  ) -> None:
    """Applies a given transformation to the left of all values issued by the trajectory."""
    ...

  def get_R_world_trunk(
    self: WalkTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def get_T_world_left(
    self: WalkTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def get_T_world_right(
    self: WalkTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def get_a_world_CoM(
    self: WalkTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def get_j_world_CoM(
    self: WalkTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def get_next_support(
    self: WalkTrajectory,
    t: float, # double
    n: int = 1, # int

  ) -> Support:
    """Returns the nth next support corresponding to the given time in the trajectory."""
    ...

  def get_p_world_CoM(
    self: WalkTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  def get_p_world_DCM(
    self: WalkTrajectory,
    t: float, # double
    omega: float, # double

  ) -> numpy.ndarray:
    ...

  def get_p_world_ZMP(
    self: WalkTrajectory,
    t: float, # double
    omega: float, # double

  ) -> numpy.ndarray:
    ...

  def get_part_t_start(
    self: WalkTrajectory,
    t: float, # double

  ) -> float:
    """Returns the trajectory time start for the support corresponding to the given time."""
    ...

  def get_prev_support(
    self: WalkTrajectory,
    t: float, # double
    n: int = 1, # int

  ) -> Support:
    """Returns the nth previous support corresponding to the given time in the trajectory."""
    ...

  def get_support(
    self: WalkTrajectory,
    t: float, # double

  ) -> Support:
    """Returns the support corresponding to the given time in the trajectory."""
    ...

  def get_supports(
    self: WalkTrajectory,

  ) -> list[Support]:
    ...

  def get_v_world_CoM(
    self: WalkTrajectory,
    t: float, # double

  ) -> numpy.ndarray:
    ...

  jerk_planner_timesteps: int # int

  def support_is_both(
    self: WalkTrajectory,
    t: float, # double

  ) -> bool:
    ...

  def support_side(
    self: WalkTrajectory,
    t: float, # double

  ) -> any:
    ...

  t_end: float # double

  t_start: float # double


class WheelTask:
  A: numpy.ndarray # Eigen::MatrixXd
  """Matrix A in the task Ax = b, where x are the joint delta positions. 
        """

  T_world_surface: numpy.ndarray # Eigen::Affine3d
  """Target position in the world. 
        """

  def __init__(
    self: WheelTask,
    joint: str, # std::string
    radius: float, # double
    omniwheel: bool = False, # bool

  ) -> any:
    """See KinematicsSolver::add_wheel_task."""
    ...

  b: numpy.ndarray # Eigen::MatrixXd
  """Vector b in the task Ax = b, where x are the joint delta positions. 
        """

  def configure(
    self: WheelTask,
    name: str, # std::string
    priority: any, # placo::kinematics::ConeConstraint::Priority
    weight: float = 1.0, # double

  ) -> None:
    """Configures the object. 
        

    :param name: task name 

    :param priority: task priority (hard, soft or scaled) 

    :param weight: task weight"""
    ...

  def error(
    self: WheelTask,

  ) -> numpy.ndarray:
    """Task errors (vector) 
        

    :return: task errors"""
    ...

  def error_norm(
    self: WheelTask,

  ) -> float:
    """The task error norm. 
        

    :return: task error norm"""
    ...

  joint: str # std::string
  """Frame. 
        """

  name: str # std::string
  """Object name. 
        """

  omniwheel: bool # bool
  """Omniwheel (can slide laterally) 
        """

  priority: any # placo::kinematics::ConeConstraint::Priority
  """Object priority. 
        """

  radius: float # double
  """Wheel radius. 
        """

  def update(
    self: WheelTask,

  ) -> None:
    """Update the task A and b matrices from the robot state and targets."""
    ...


def flatten_on_floor(
  transformation: numpy.ndarray, # const Eigen::Affine3d &

) -> numpy.ndarray:
  """Takes a 3D transformation and ensure it is "flat" on the floor (setting z to 0 and keeping only yaw) 
        

  :param transformation: a 3D transformation 

  :return: a 3D transformation that lies on the floor (no pitch/roll and no z)"""
  ...


def frame_yaw(
  rotation: numpy.ndarray, # Eigen::Matrix3d

) -> float:
  """Computes the "yaw" of an orientation. 
        

  :param rotation: the orientation 

  :return: a scalar angle [rad]"""
  ...


def getNumpyType(

) -> any:
  ...


def get_classes_registry(

) -> any:
  ...


def interpolate_frames(
  frameA: numpy.ndarray, # Eigen::Affine3d
  frameB: numpy.ndarray, # Eigen::Affine3d
  AtoB: float, # double

) -> numpy.ndarray:
  """Interpolate between two frames. 
        

  :param frameA: Frame A 

  :param frameB: Frame B 

  :param AtoB: A real number from 0 to 1 that controls the interpolation (0: frame A, 1: frameB) 

  :return:"""
  ...


class map_indexing_suite_map_string_double_entry:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def data(
    arg1: map_indexing_suite_map_string_double_entry,

  ) -> float:
    ...

  def key(
    arg1: map_indexing_suite_map_string_double_entry,

  ) -> str:
    ...


class map_string_double:
  def __init__(
    arg1: object,

  ) -> None:
    ...


def rotation_from_axis(
  axis: str, # std::string
  vector: numpy.ndarray, # Eigen::Vector3d

) -> numpy.ndarray:
  """Builds a rotation matrix with a given axis target. 
        

  :param axis: axis (x, y or z) 

  :param vector: target (unit) vector 

  :return: 3x3 rotation matrix"""
  ...


def seed(
  seed_value: int,

) -> None:
  ...


def setNumpyType(
  numpy_type: object,

) -> None:
  ...


def sharedMemory(
  value: bool,

) -> None:
  ...


def switchToNumpyArray(

) -> any:
  ...


def switchToNumpyMatrix(

) -> any:
  ...


class vector_Collision:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: vector_Collision,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: vector_Collision,
    arg2: object,

  ) -> None:
    ...


class vector_Distance:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: vector_Distance,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: vector_Distance,
    arg2: object,

  ) -> None:
    ...


class vector_MatrixXd:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: vector_MatrixXd,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: vector_MatrixXd,
    arg2: object,

  ) -> None:
    ...


class vector_Vector2d:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: vector_Vector2d,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: vector_Vector2d,
    arg2: object,

  ) -> None:
    ...


class vector_Vector3d:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: vector_Vector3d,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: vector_Vector3d,
    arg2: object,

  ) -> None:
    ...


class vector_double:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: vector_double,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: vector_double,
    arg2: object,

  ) -> None:
    ...


class vector_int:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: vector_int,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: vector_int,
    arg2: object,

  ) -> None:
    ...


class vector_string:
  def __init__(
    arg1: object,

  ) -> None:
    ...

  def append(
    arg1: vector_string,
    arg2: object,

  ) -> None:
    ...

  def extend(
    arg1: vector_string,
    arg2: object,

  ) -> None:
    ...


def wrap_angle(
  angle: float, # double

) -> float:
  """Wraps an angle between -pi and pi."""
  ...


__groups__ = {'placo::dynamics': ['AvoidSelfCollisionsDynamicsConstraint', 'Contact', 'Contact6D', 'DynamicsCoMTask', 'DynamicsConstraint', 'DynamicsFrameTask', 'DynamicsGearTask', 'DynamicsJointsTask', 'DynamicsOrientationTask', 'DynamicsPositionTask', 'DynamicsReactionRatioConstraint', 'DynamicsRelativeFrameTask', 'DynamicsRelativeOrientationTask', 'DynamicsRelativePositionTask', 'DynamicsSolver', 'DynamicsSolverResult', 'DynamicsTask', 'DynamicsTorqueTask', 'ExternalWrenchContact', 'PointContact', 'PuppetContact', 'Relative6DContact', 'RelativePointContact', 'TaskContact'], 'placo::kinematics': ['AvoidSelfCollisionsKinematicsConstraint', 'AxisAlignTask', 'CentroidalMomentumTask', 'CoMPolygonConstraint', 'CoMTask', 'ConeConstraint', 'DistanceTask', 'FrameTask', 'GearTask', 'JointsTask', 'KinematicsConstraint', 'KinematicsSolver', 'KineticEnergyRegularizationTask', 'OrientationTask', 'PositionTask', 'RegularizationTask', 'RelativeFrameTask', 'RelativeOrientationTask', 'RelativePositionTask', 'Task', 'WheelTask'], 'placo::tools': ['AxisesMask', 'CubicSpline', 'CubicSpline3D', 'Prioritized'], 'placo::model': ['Collision', 'Distance', 'RobotWrapper', 'RobotWrapper_State'], 'placo::problem': ['Expression', 'Integrator', 'IntegratorTrajectory', 'PolygonConstraint', 'Problem', 'ProblemConstraint', 'QPError', 'Sparsity', 'SparsityInterval', 'Variable'], 'placo::humanoid': ['Footstep', 'FootstepsPlanner', 'FootstepsPlannerNaive', 'FootstepsPlannerRepetitive', 'HumanoidParameters', 'HumanoidRobot', 'LIPM', 'LIPMTrajectory', 'Support', 'SwingFoot', 'SwingFootCubic', 'SwingFootCubicTrajectory', 'SwingFootQuintic', 'SwingFootQuinticTrajectory', 'SwingFootTrajectory', 'WalkPatternGenerator', 'WalkTasks', 'WalkTrajectory']}
