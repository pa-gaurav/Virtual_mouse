# Virtual_mouse_control
Controlling Mouse cursor with hand gestures using Computer vision, Machine learning and Artificial Intelligence.

This project stimulates a physical mouse which performs all the functions performed by a mouse corresponding to your hand movements and gestures. i.e., the webcam/camera captures your video using OpenCV a library of programming functions mainly aimed at real-time computer vision. and detect your hands using mediapipe a cross-platform library developed by Google that provides amazing ready-to-use ML solutions for computer vision tasks and depending on your hand gestures and fingers position, you can move the cursor and perform left click, right click, drag, select and scroll up and down.

1. For simple cursor movement- Index finger up, other fingers down.

2. For Left click- Distance between tip of Index and Middle fingers should be less then 30 mm other fingers down.

3. For Right click and select- Distance between tip of Thumb and Index finger should be less then 30 mm other fingers down.

4. For Dragging- Using selecting (Step-3) and then moving cursor (Step-1).

5. For Dropping- Index and ring ginger should be up and others down.

6. For Scrolling up- All fingers up, thumb dowm.

7. For Scrolling down- All fingers down, thumb up.

8. For Exiting- Alll fingers up except middle finger.

These various mouse function are accessible by using PyAutoGUI a Python package that works across Windows, MacOS X and Linux which provides the ability to simulate mouse cursor moves and clicks as well as keyboard button presses.
