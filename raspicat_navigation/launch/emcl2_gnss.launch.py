import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, TimerAction
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node, SetParameter


def generate_launch_description():
    emcl2_params_file = LaunchConfiguration('emcl2_params_file')
    gnss2map_params_file = LaunchConfiguration('gnss2map_params_file')
    map_yaml_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    map_topic_name = LaunchConfiguration('map_topic_name')
    namespace = LaunchConfiguration('namespace')
    
    cnf_dir = os.path.join(get_package_share_directory('raspicat_navigation'), 'config')
    param_dir = os.path.join(cnf_dir, 'param')

    declare_map_yaml = DeclareLaunchArgument(
        'map',
        default_value=[
            TextSubstitution(text=os.path.join(
                cnf_dir, 'map', 'tsudanuma_campus', 'localization', 'map_tsudanuma_campus.yaml'))],
        description='Full path to map yaml file to load')
    
    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')
    
    declare_emcl2_params_file = DeclareLaunchArgument(
        'emcl2_params_file',
        default_value=[
            TextSubstitution(text=os.path.join(param_dir, 'emcl2.param.yaml'))],
        description='emcl2 param file path')
    
    declare_gnss2map_params_file = DeclareLaunchArgument(
        'gnss2map_params_file',
        default_value=[
            TextSubstitution(text=os.path.join(param_dir, 'gnss_tsudanuma.param.yaml'))],
        description='gnss2map in tsudanuam campus param file path')
    
    declare_map_topic_name = DeclareLaunchArgument(
        'map_topic_name', 
        default_value=TextSubstitution(text='map/localization'), 
        description='map topic name'
    )
    
    declare_namespace = DeclareLaunchArgument(
        'namespace', 
        default_value=TextSubstitution(text='')
    )

    lifecycle_nodes = ['map_server']
    emcl2_map_topic = (namespace, '/', map_topic_name)
    launch_node = GroupAction(
        actions=[
            SetParameter('use_sim_time', use_sim_time),
            Node(
                name='emcl2',
                package='emcl2',
                executable='emcl2_node',
                parameters=[emcl2_params_file],
                output='screen', 
                remappings=[('map', map_topic_name)]
                ),
            Node(
                name='gauss_kruger_node',
                package='gnss2map',
                executable='gauss_kruger_node',
                parameters=[gnss2map_params_file],
                output='screen', 
                ),
            TimerAction(
                period=1.0, 
                actions=[
                    Node(
                        namespace=namespace,
                        package='nav2_map_server',
                        executable='map_server',
                        name='map_server',
                        parameters=[{'yaml_filename': map_yaml_file}],
                        output='screen', 
                        remappings=[('map', map_topic_name)]
                    )
                ]
            ),
            Node(
                namespace=namespace, 
                package='nav2_lifecycle_manager',
                executable='lifecycle_manager',
                name='lifecycle_manager_localization',
                output='screen',
                parameters=[{'autostart': True},
                            {'node_names': lifecycle_nodes}])
        ]
    )
    
    rviz_config_file = os.path.join(get_package_share_directory('raspicat_navigation'), 
                                    'config', 'rviz', 'nav2.rviz')
    rviz2 = Node(package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        ros_arguments=['--log-level', 'error'],
    )

    ld = LaunchDescription()
    ld.add_action(declare_map_topic_name)
    ld.add_action(declare_map_yaml)
    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_emcl2_params_file)
    ld.add_action(declare_gnss2map_params_file)
    ld.add_action(declare_namespace)

    ld.add_action(launch_node)
    ld.add_action(rviz2)

    return ld
