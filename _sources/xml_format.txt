A Writing3D Tutorial
======================

Welcome to Writing3D! This software is a tool for programmers and artists alike, enabling its users to easily create stunning displays of text, shape, and color within a virtual reality atmosphere. Projects are based on the open source 3D rendering engine Blender, allowing users to have full creative control over their work. These docs will provide an introduction to the software as a whole, installation, and the process of creating a project, as well as some of the features at your fingertips. 

***************
Installation
***************

Before getting into installation and projects, ensure that you have Python3 downloaded. This is necessary because Writing3D is based in Blender, which uses Python3 as a scripting language. Regardless of whether you intend to code new features for Writing3D or create projects, installation of Python3 is absolutely necessary. After this is complete, simply run the following script from your terminal:

``python3 setup.py –install –user``

This will install Blender onto your computer, and give you access to the world of Writing3D!

*****************
Roots and Set-up
*****************
    
    User input is provided to Writing3D through the use of XML documents. At the highest point in the tag hierarchy is the ``<Story>`` tag. Within these, we have the ``<ObjectRoot>`` tags, in which we will define all objects in the scene (continue reading for more on how to do that!) We also have ``<PlacementRoot>`` in which we define the Center and Walls of the specific virtual reality theater we are using. For Brown's CAVE, we have the following:

``<PlacementRoot>``
              
    ``<Placement name="Center">``
                     
        ``<RelativeTo>Center</RelativeTo>``
                    
        ``<Position>(0.0, 0.0, 0.0)</Position>``
                            
            ``<Axis rotation="(0.0, 1.0, 0.0)" angle="0.0"/>``
              
    ``</Placement>``
     
    ``<Placement name="FrontWall">``
                     
        ``<RelativeTo>Center</RelativeTo>``
                     
        ``<Position>(0.0, 0.0, -4.0)</Position>``
                           
            ``<LookAt target="(0.0, 0.0, 0.0)" up="(0.0, 1.0, 0.0)"/>``
              
    ``</Placement>``
              
    ``<Placement name="LeftWall">``
                     
        ``<RelativeTo>Center</RelativeTo>``
                     
        ``<Position>(-4.0, 0.0, 0.0)</Position>``
                            
            ``<LookAt target="(0.0, 0.0, 0.0)" up="(0.0, 1.0, 0.0)"/>``
              
    ``</Placement>``
              
    ``<Placement name="RightWall">``
                     
        ``<RelativeTo>Center</RelativeTo>``
                     
        ``<Position>(4.0, 0.0, 0.0)</Position>``
                            
            ``<LookAt target="(0.0, 0.0, 0.0)" up="(0.0, 1.0, 0.0)"/>``
              
    ``</Placement>``
              
    ``<Placement name="FloorWall">``
                     
        ``<RelativeTo>Center</RelativeTo>``
                     
        ``<Position>(0.0, -4.0, 0.0)</Position>``
                            
            ``<LookAt target="(0.0, 0.0, 0.0)" up="(0.0, 0.0, -1.0)"/>``
              
    ``</Placement>``
       
``</PlacementRoot>``

The contents of the ``<PlacementRoot>`` tags are unique to the VR theater, but once determined, they can be copy and pasted onto your XML!

We also have the option to create ``<TimelineRoot>`` and ``<GroupRoot>`` tags, which we'll get into later. 

At the end of our file at the same indentation of the ``Roots``, before the closing ``</Story>`` tag, we define several housekeeping options for setting up the scene, such as if the user can rotate or move, the camera position, and the background color, within ``<Global>`` tags.

``<Global>``
         
    ``<CameraPos far-clip="100.0">``
                    
        ``<Placement>``
                            
            ``<RelativeTo>Center</RelativeTo>``
                            
            ``<Position>(0.0, 0.0, 6.0)</Position>``
                     
        ``</Placement>``
              
    ``</CameraPos>``
              
    ``<CaveCameraPos far-clip="100.0">``
                     
        ``<Placement>``
                            
            ``<RelativeTo>Center</RelativeTo>``
                            
            ``<Position>(0.0, 0.0, 0.0)</Position>``
                     
        ``</Placement>``
              
    ``</CaveCameraPos>``
                     
    ``<Background color="0, 0, 0"/>``
              
    ``<WandNavigation allow-rotation="true" allow-movement="true"/>``
       
``</Global>``

So, the high-level tags of a program will look a bit like this:

``<Story>``

    ``<ObjectRoot>``
        
       `` //Create objects here!``

    ``</ObjectRoot>``

    ``<GroupRoot>``

        ``//Put objects into groups here!``

    ``</GroupRoot>``

    ``<TimelineRoot>``

        ``//Set up timelines here!``

    ``</TimelineRoot>``

    ``<PlacementRoot>``

        ``//Define walls here!``

    ``</PlacementRoot>``

    ``<Global>``

        ``//Housekeeping options here!``

    ``</Global>``

``</Story>``

***************
Features
***************
The Object Class
******************

Writing3D is coded with an overarching W3DObject superclass that controls several characteristics available to objects: visibility, color, lighting, scale, and so on. We’ll go over creating an object and setting all of these values and more. First, we’ll give the Object a name so we and Writing3D can reference it later.

``<Object name = “My Object”>``

``</Object>``

Color, Visibility, and Scale:

Within these tags, we can set our objects visibility to True or False, and Color based on red, green, and blue values between 0 and 255. The Scale feature allows us to define a size of the object, with 1.0 referring to the normal size and higher numbers increasing the size based on the inputted number.

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Scale> 1.0 </Scale>``

``</Object>``

Placement:

Next, we choose a  starting position for our object in the scene. The Placement option comes with two sub-options, “RelativeTo” and “Position.” Essentially, we choose a specific wall of the 3D scene (LeftWall, RightWall, etc.) or the Center of the scene, to input into RelativeTo. The Position is an ordered pair of the form (x, y, z) to place the object in relation to the selected RelativeTo position.

Let’s have our object be -2 units away horizontally from the center of the scene, but on the same y and z axes. This can be represented by the location: (-2.0, 0.0, 0.0). We add this to our growing object tag.

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``

        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(-2.0,0.0,0.0)</Position>``

    ``</Placement>``

``</Object>``

And lastly, we handle three options: ClickThrough, AroundSelfAxis, and Lighting. If two objects overlap, setting ClickThrough to true allows a click the top object to also register for the bottom object. Setting AroundSelfAxis to true will allow the object to rotate around its own midpoint axis rather than its top left corner. Lighting determines if an object responds to external lighting; if set to false, an object will emit its own light and be visible even in the presence of no external light source.

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Lighting> false </Lighting>``

    ``<ClickThrough> false </ClickThrough>``

    ``<AroundSelfAxis> false </AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``

        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(-2.0,0.0,0.0)</Position>``

    ``</Placement>``

``</Object>``

Content:

The last step is to actually define what we’re creating. We do this with the content option, and have several choices: text, lamps, linked objects, models, images, shapes—all of which will be discussed in detail. For now, let’s elide the specifics and simply add Content tags to our code. 

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Lighting> false </Lighting>``

    ``<ClickThrough> false </ClickThrough>``

    ``<AroundSelfAxis> false </AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(-2.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``//elided``

    ``</Content>``

``</Object>``

The next section will discuss what we can do by inputting into that elided space between the content tags! 

The Content Class
******************

Text
^^^^^^^^^^^^^^^^^^^^^
You can add strings of text to the 3D scene using this feature. The Text call relies on five changeable options: the actual text, the horizontal alignment, the vertical alignment, the type of font, and the depth. In the following example, we replicate the basic example that comes with Writing3D by creating a text object of the string “Hello World!”

We will set horizontal and vertical alignment simply to “center”, and choose our font to be Courier.tff. Within <text> and </text> tags, we add the actual string that we’re writing, as so:

``<Text horiz-align= “center” vert-align = “center” font= “Courier.ttf” depth = “0.0”>``

    ``<text>Hello World!</text>``

``</Text>``

A depth of 0.0 sets the text to be created on a 2D plane. To make the text three dimensional, we can set depth at a higher number. If we shine a lamp on the object created in the following code, we’ll be able to see light and shadow reacting to the edges of the text:

``<Text horiz-align= “center” vert-align = “center” font= “Courier.ttf” depth = “3.0”>``

    ``<text>Hello World!</text>``

``</Text>``

By adding this to our object code, we’ve created our first object!

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Lighting> false </Lighting>``

    ``<ClickThrough> false </ClickThrough>``

    ``<AroundSelfAxis> false </AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(-2.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Text horiz-align= “center” vert-align = “center” font= “Courier.ttf” depth = “3.0”>``

                ``<text>Hello World!</text>``

            ``</Text>``

    ``</Content>``

``</Object>``

Lamps and Light Sources
^^^^^^^^^^^^^^^^^^^^^^^^
The Blender interface used to create the immersive Writing3D projects begins by creating an initial lamp. Additional light sources are easy to add and can lead to some beautiful effects when rendered! We begin with some choices. Writing3D allows us to specify if our light is specular or diffuse, the angle in degrees, and its constant, linear, and quadratic attenuations. If the light is a Spotlight (more on that in a second), we can also specify the angle in degrees specifying its spread. 

Let’s create a basic light source.

``<Light diffuse="true" specular="true" const_atten="1.0" lin_atten="0.0" quad_atten="0.0">``
	
``</Light>``

The only thing left to do is decide what type of light source we want. The Blender game engine offers us three options: Point Light, Directional Light, and Spot Light. We specify this in a tag within the <Light></Light> tags, like so:

``<Light diffuse="true" specular="true" const_atten="1.0" lin_atten="0.0" quad_atten="0.0">``

    ``<Point/>``
	
``</Light>``

Alternatively, we can use ``<Spot/>`` or ``<Directional/>`` to create the other types of light as well.

Lamps are created with the same options as the basic object. So, we can specify color, position, visibility, and so on much in the same way as we did while creating text. If we want to create a red point light positioned near the center of the scene, for instance, we simply make those adjustments to the object’s color option in the following manner.

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Lighting> false </Lighting>``

    ``<ClickThrough> false </ClickThrough>``

    ``<AroundSelfAxis> false </AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(-2.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Light diffuse="true" specular="true" const_atten="1.0" lin_atten="0.0" quad_atten="0.0">``

                ``<Point/>``
	
           ``</Light>``

    ``</Content>``

``</Object>``

Shapes
^^^^^^^^^^^^^^^^^^^^^
Next step, adding 3D shapes to the scene. Writing3D allows us to create Spheres, Cubes, Cones, Cylinders, and—interestingly—a Monkey Head. The process is very similar to creating a light source. 

We begin by deciding the shape that we want, and it’s size, defined as it’s radius. If our shape is a Cone or a Cylinder, we can also define it’s depth—how long it will be. To create a Cube, we have:

``<Shape shape_type= “Cube” radius = “0.5”/>``

To create a Cylinder with a height of 4, we have:

``<Shape shape_type= “Cylinder” radius= “0.5” depth= “4”/>``

Each shape goes within the ``<Content>`` tags of its own ``<Object>`` tag. So to add our cube to the scene, we have:

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Lighting> false </Lighting>``

    ``<ClickThrough> false </ClickThrough>``

    ``<AroundSelfAxis> false </AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(-2.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Shape shape_type= “Cube” radius = “0.5”/>``

    ``</Content>``

``</Object>``

Our choices for shapes are ``Cube``, ``Cylinder``, ``Sphere``, ``Cone``, and ``Monkey``.


Imported Images
^^^^^^^^^^^^^^^^^^^^^
Writing3D supports imported images of type .jpg. Simply adding the file path name to an Image tag will do the trick.

``<Image filename=”./pictures/MyVirtualPic.jpg”/>``

Placing this between the content tags, we can complete the process! Note that the color tags here will not affect the picture, and are simply there for formality.

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Lighting> false </Lighting>``

    ``<ClickThrough> false </ClickThrough>``

    ``<AroundSelfAxis> false </AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(-2.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Image filename=”./pictures/MyVirtualPic.jpg”/>``

    ``</Content>``

``</Object>``

Imported Models
^^^^^^^^^^^^^^^^^^^^^
**check collisions**

To display imported three-dimensional models, we follow a process similar to importing pictures, but add detail about checking collisions. So, we have:

``<Model filename=”./models/myModel.obj” check-collisions= “false”/>``

And, of course, we add the rest of the object code. Again, the color tags are simply here as formality and are not necessary.

``<Object name = “My Object”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 0 </Color>``

    ``<Lighting> false </Lighting>``

    ``<ClickThrough> false </ClickThrough>``

    ``<AroundSelfAxis> false </AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(-2.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Model filename=”./models/myModel.obj” check-collisions= “false”/>``

    ``</Content>``

``</Object>``


Now we’ve got the object class spelled out. These are the building blocks for anything we create in Writing3D. In the next section, we’ll run through a simple tutorial showing just what we can do with these objects; using Links and/or Timelines, we bring all our objects to life.


Links/LinkRoots
^^^^^^^^^^^^^^^^^^^^^

Links can be used to add movement and transitions to Writing3D projects. We'll get into a more in depth example in a second. For now, this is the general set-up for a ``Text`` object that has been into a ``Link``. Notice that ``<LinkRoot>``, which makes an ``Object`` a ``Link``, is at the same hierarchy as the ``<Content>`` tags.

``<Object name = “MyLink”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 255 </Color>``

    ``<Lighting>false</Lighting>``

    ``<ClickThrough>false</ClickThrough>``

    ``<AroundSelfAxis>false</AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(0.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Text horiz-align= “center” vert-align = “center” font= “Courier.ttf” depth = “0.0”>``

                ``<text>Link Text!</text>``

            ``</Text>``

    ``</Content>``

    ``<LinkRoot>``

        ``<Link>``

            ``//code to make object move!``

        ``</Link>``

    ``</LinkRoot>``

``</Object>``

********************************
Hello World, an Extended Example
********************************

Here, we’ll make a “Hello World” text object that sits on the left wall of the virtual reality theater. On the click of a link, the text will move to the front wall. We start with the same Object code as before to create our “Hello World” object:


``<Object name = “movingtext”>``

    ``<Visible> true </Visible>``

    ``<Color> 153, 153, 153 </Color>``

    ``<Lighting>false</Lighting>``

    ``<ClickThrough>false</ClickThrough>``

    ``<AroundSelfAxis>false</AroundSelfAxis>``

    ``<Scale> 6.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>LeftWall</RelativeTo>``

        ``<Position>(0.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Text horiz-align= “center” vert-align = “center” font= “Courier.ttf” depth = “0.0”>``

                ``<text>Hello World!</text>``

            ``</Text>``

    ``</Content>``

``</Object>``

Notice that this is positioned on the Left Wall, its starting position.
Next, we rewrite our code for Links in the following way:

``<Object name = “frontlink”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 255 </Color>``

    ``<Lighting>false</Lighting>``

    ``<ClickThrough>false</ClickThrough>``

    ``<AroundSelfAxis>false</AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(0.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Text horiz-align= “center” vert-align = “center” font= “Courier.ttf” depth = “0.0”>``

                ``<text>Fly Front!</text>``

            ``</Text>``

    ``</Content>``

    ``<LinkRoot>``

        ``<Link>``

            ``//code to make object move!``

        ``</Link>``

    ``</LinkRoot>``

``</Object>``

We fill in the Link code to give it instructions on what to do when clicked. First, we must enable the Link. We can also choose a color for the link to turn when being hovered over within the “Enabled Color” tags, and a color for the link to turn when selected in the “Selected Color” tags.

``<Link>``
    ``<Enabled>true</Enabled>``

    ``<Remain Enabled>true</Remain Enabled>``

    ``<EnabledColor>0,128,255</EnabledColor>``

    ``<SelectedColor>255,0,0</SelectedColor>``

    ``//further code coming up!``

``</Link>``

Within “Action” tags, we specify just how the link can change the scene. Within these tags, we specify what object will be changed in the “ObjectChange” tag—in this case, it’s our “Hello World” object, which we named “moving text.” We specify a duration for our change, the type of change, and specifics to the type of change. 

``<Actions>``

	``<ObjectChange name = “movingtext”>``

		``<Transition duration = “1.0”>``

			``//Type of change!``

		``</Transition>``

	``</ObjectChange>``

``</Actions>``

We want the “movingtext” object to move when this link is selected. So, the type of change will be recorded within “Movement” tags. We then specify where the object will move to within “Placement” tags, in a very similar way to how we initially set up placement when creating our objects. It looks like this:

``<Actions>``

	``<ObjectChange name = “movingtext”>``

		``<Transition duration = “1.0”>``

			``<Movement>``

				``<Placement>``
				    ``<RelativeTo>FrontWall</RelativeTo>``

				      ``<Position>(0.0,0.0,0.0)</Position>``

                  ``</Placement>``

			``</Movement>``

		``</Transition>``

	``</ObjectChange>``

``</Actions>``

We can add additional actions that will take place at the same time the link is clicked. These would go in action tags and each ``<Action>`` would be listed one after the other. So, we can add another ``<Action>`` to, say, change the color of the text as well to (0,100,0).

Putting it all together:


``<Object name = “movingtext”>``

    ``<Visible> true </Visible>``

    ``<Color> 153, 153, 153 </Color>``

    ``<Lighting>false</Lighting>``

    ``<ClickThrough>false</ClickThrough>``

    ``<AroundSelfAxis>false</AroundSelfAxis>``

    ``<Scale> 6.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>LeftWall</RelativeTo>``

        ``<Position>(0.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Text horiz-align= “center” vert-align = “center” font= “Courier.ttf” depth = “0.0”>``

                ``<text>Hello World!</text>``

            ``</Text>``

    ``</Content>``

``</Object>``

``<Object name = “frontlink”>``

    ``<Visible> true </Visible>``

    ``<Color> 255, 255, 255 </Color>``

    ``<Lighting>false</Lighting>``

    ``<ClickThrough>false</ClickThrough>``

    ``<AroundSelfAxis>false</AroundSelfAxis>``

    ``<Scale> 1.0 </Scale>``

    ``<Placement>``
        ``<RelativeTo>Center</RelativeTo>``

        ``<Position>(0.0,0.0,0.0)</Position>``

    ``</Placement>``

    ``<Content>``

            ``<Text horiz-align= “center” vert-align = “center” font= “Courier.ttf” depth = “0.0”>``

                ``<text>Fly Front!</text>``

            ``</Text>``

    ``</Content>``

    ``<LinkRoot>``

       ``<Link>``

           ``<Enabled>true</Enabled>``

            ``<Remain Enabled>true</Remain Enabled>``

            ``<EnabledColor>0,128,255</EnabledColor>``

            ``<SelectedColor>255,0,0</SelectedColor>``

            ``<Actions>``

	            ``<ObjectChange name = “movingtext”>``

		        ``<Transition duration = “1.0”>``

			        ``<Movement>``

				        ``<Placement>``
				            ``<RelativeTo>FrontWall</RelativeTo>``

				             ``<Position>(0.0,0.0,0.0)</Position>``

                          ``</Placement>``

			        ``</Movement>``

		        ``</Transition>``

	        ``</ObjectChange>``

        ``</Actions>``

        ``<Actions>``
	
            ``<ObjectChange name= “frontlink”>``
		
                ``<Transition duration= “1.0”>``
			
                    ``<Color>0,100,0</Color>``
		
                ``</Transition>``

	    ``</ObjectChange>``

        ``</Actions>``

        ``</Link>``

    ``</LinkRoot>``

``</Object>``

All of this code defines the ``Objects`` of the scene, and so would go within ``<ObjectRoot> </ObjectRoot>`` tags.

Let’s stop for a checkpoint here. By now, you should have a good understanding of how to use the Object class, how to set up several objects in a scene, and how to apply links to change the state of a scene. In the next bit, we’ll move on to more complex items: Timelines and Groups.

Timelines
*********************

In our Hello World example, we used a links to achieve two ObjectChanges in order. Another way to handle changing objects is through Timelines. Unlike links, Timelines can begin right at the start of the program. They can also facilitate random movement and changes that happen in continuous or numbered loops. Additionally, they create sequential ``<ObjectChange>``s while link ``<Actions>`` will all occur at the same time that the link is clicked. 

We start by setting up ``<TimelineRoot>`` tags. These will be at the same level in hierarchy as ``<ObjectRoot>``. Within these, we set up ``<Timeline>`` tags where we name our timeline and have the option to start the timeline immediately. For now, we’ll have the timeline start right from the start of the program. Timelines can also start within other timelines, or when clicking a link.

The next step is to choose the delay from the moment the timeline begins that the transition will begin. This will come in handy when stringing many transitions together in one timeline. Let’s choose to wait 0.5 seconds.

``<TimelineRoot>``

    ``<Timeline name=“MyTimeline” start-immediately=“true”>``

        ``<TimedActions seconds-time= “0.5”>``

            ``//elided``

        ``</TimedActions>``

    ``</Timeline>``

``<TimelineRoot>``


We now have to define which object we are changing within <ObjectChange> tags, a duration, and a type of change. This is very similar to the Link code we wrote in our Hello World example. Let’s extend that example to this, and have our “Hello World!” text change color from the original gray (153, 153, 153) to bright yellow (255, 255, 0). Recall that the name of our “Hello World!” text object was “movingtext”.

``<TimelineRoot>``

    ``<Timeline name=“MyTimeline” start-immediately=“true”>``

        ``<TimedActions seconds-time= “0.0”>``

            ``<ObjectChange name="movingtext>"``

                ``<Transition duration="1.0">``

                    ``<Color>255,255,0</Color>``

                ``</Transition>``

            ``</ObjectChange>``

        ``</TimedActions>``

    ``</Timeline>``

``<TimelineRoot>``

This simple Timeline will change the color of “Hello World!” from gray to yellow the moment the program starts. 

Now, let’s try something else. Instead of having “Hello World!” change color, we’ll have it change position as we did in the example. This time, however, it’ll change position relative to its old position, and will loop through this movement for the duration of the project. Let’s set up our Timeline again. In this case, the type of object change is Movement, but more specifically, ``<MoveRel>``, which tells Writing3D to move the object relative to its old position. The first movement will be relative to the area of the scene we will label within ``<Placement>`` tags (RightWall, FrontWall, Center, etc); further movements will be incremented from the previous position by the number in ``<Position>`` tags.

``<TimelineRoot>``

    ``<Timeline name=“MyTimeline” start-immediately=“true”>``

        ``<TimedActions seconds-time= “0.0”>``

            ``<ObjectChange name="movingtext>"``

                ``<Transition duration="1.0">``

                    ``<MoveRel>``

                        ``<Placement>``

                            ``<RelativeTo>Center</RelativeTo>``

                            ``<Position>(0,0,2)</Position>``

                        ``</Placement>``

                ``</Transition>``

            ``</ObjectChange>``

        ``</TimedActions>``

    ``</Timeline>``

``<TimelineRoot>``


This will set up the very first movement, where “Hello World!” will move 2 units forward from the Center. Since we’re taking advantage of <MoveRel>, we’d like this to happen several more times by looping the Timeline. This is another type of TimedAction. The delay in this case should be the time it takes for the previous Transition to occur: 1 second, plus that 0.5 second delay we stacked on at the beginning.
Rather than an ObjectChange, we use a TimerChange and indicate the name of the timeline that we are changing. Then we invoke a <start/> command to start or restart the timeline.

``<TimedActions seconds-time=”1.5”>``

    ``<TimerChange name = “Looping Timeline”>``

        ``<start/>``

    ``</TimerChange>``

``</TimedActions>``

Putting it all together, we have: 

``<TimelineRoot>``

    ``<Timeline name=“MyTimeline” start-immediately=“true”>``

        ``<TimedActions seconds-time= “0.0”>``

            ``<ObjectChange name="movingtext>"``

                ``<Transition duration="1.0">``

                    ``<MoveRel>``

                        ``<Placement>``

                            ``<RelativeTo>Center</RelativeTo>``

                            ``<Position>(0,0,2)</Position>``

                        ``</Placement>``

                ``</Transition>``

            ``</ObjectChange>``

        ``</TimedActions>``

        ``<TimedActions seconds-time=”1.5”>``

            ``<TimerChange name = “Looping Timeline”>``

                ``<start/>``

            ``</TimerChange>``

        ``</TimedActions>``

    ``</Timeline>``

``<TimelineRoot>``

Groups
******************

We’ve finished how objects are created and changed. The Grouping feature allows us to control objects’ relationships to each other, allowing us to enact an ObjectChange on several objects at once, or on one chosen randomly.

Let’s say we have two objects placed next to each other. One is our ``“moving text”`` Hello World! object from before, and one is a sphere called ``“my-sphere.”`` As before, we want an object to move forward by 2 units each time, as we did in our previous ``Looping Timeline`` example. However, rather than just applying this to “movingtext” we’d like Writing3D to randomly choose either “movingtext” or “my-sphere” then move the selected object.

The first thing to do is put the objects in our selection pool within their own group. This occurs at the same hierarchy as ``<ObjectRoot>`` and ``<TimelineRoot>``: we define all our groups within ``<GroupRoot>``. We then give the Group a name within ``<Group>`` tags and we use <Object> tags to add whatever objects we’d like to “MyGroup” by name.

``<GroupRoot>``

    ``<Group name= “MyGroup”>``

        ``<Objects name= “movingtext”/>``

        ``<Objects name= “my-sphere”/>``

    ``</Group>``

``</GroupRoot>``

Now, let’s repurpose the code we wrote to loop timelines, with a key difference. Here, instead of an ``<ObjectChange>``, we are using a ``GroupChange``, defined within the ``<GroupRef>`` tags. We also indicate that we’d like one object from the group to be selected randomly as target for the transition with ``“Select One Randomly”`` under the “random” title.



``<TimedActions seconds-time= “0.0”>``

    ``<GroupRef name="MyGroup" random="SelectOneRandomly">``

        ``<Transition duration="1.0">``

            ``<MoveRel>``

                ``<Placement>``

                    ``<RelativeTo>Center</RelativeTo>``

                    ``<Position>(0,0,2)</Position>``

                ``</Placement>``

            ``</MoveRel>``

        ``</Transition>``

    ``</GroupRef>``

``</TimedActions>``

If we had defined random as ``“None”`` rather than ``“Select One Randomly,”`` this change would occur for every object in the group at once rather than just one. Putting this all together, we finish with the following code.

``<GroupRoot>``

    ``<Group name= “MyGroup”>``

        ``<Objects name= “movingtext”/>``

        ``<Objects name= “my-sphere”/>``

    ``</Group>``

``</GroupRoot>``

``<TimelineRoot>``

    ``<Timeline name="Looping Timeline" start-immediately="true">``

        ``<TimedActions seconds-time= “0.0”>``

            ``<GroupRef name="MyGroup" random="SelectOneRandomly">``

                ``<Transition duration="1.0">``

                    ``<MoveRel>``

                        ``<Placement>``

                            ``<RelativeTo>Center</RelativeTo>``

                            ``<Position>(0,0,2)</Position>``

                        ``</Placement>``

                    ``</MoveRel>``

                ``</Transition>``

            ``</GroupRef>``

        ``</TimedActions>``

        ``<TimedActions seconds-time="1.5">``

            ``<TimerChange name="Looping Timeline">``

                ``<start/>``

            ``</TimerChange>``

        ``</TimedActions>``

    ``</Timeline>``

``<TimelineRoot>``

****************
Another Example
****************


We’ve now finished going over most of the basic features Writing3D currently has to offer! Let’s wrap it all together by going through another full example. Here, we’ll have a sphere and a cube. We’ll choose one randomly to move forward relative to its old position, then choose one to move backwards relative to its old position, and then loop the timeline.

We already know how to set up ``Shape Objects``. Let’s make one yellow(255,255,0) and one white (255,255,255).

``<ObjectRoot>``

    ``<Object name = “MySphere”>``

        ``<Visible> true </Visible>``

        ``<Color> 255, 255, 0 </Color>``

        ``<Scale> 1.0 </Scale>``

        ``<Placement>``

            ``<RelativeTo>Center</RelativeTo>``

            ``<Position>(-2.0,0.0,0.0)</Position>``

        ``</Placement>``

        ``<Content>``

            ``<Shape shape_type= “Sphere” radius = “0.5”/>``

        ``</Content>``

    ``</Object>``

    ``<Object name = “MyCube”>``

        ``<Visible> true </Visible>``

        ``<Color> 255, 255, 255 </Color>``

        ``<Scale> 1.0 </Scale>``

        ``<Placement>``

            ``<RelativeTo>Center</RelativeTo>``

            ``<Position>(-2.0,0.0,0.0)</Position>``

        ``</Placement>``

        ``<Content>``

            ``<Shape shape_type= “Sphere” radius = “0.5”/>``

        ``</Content>``

    ``</Object>``

``</ObjectRoot>``

We’ll place these in a group so we can select one randomly.

``<GroupRoot>``

    ``<Group name= “MyGroup”>``

        ``<Objects name= “MySphere”/>``

        ``<Objects name= “MyCube”/>``

    ``</Group>``

``</GroupRoot>``


We reference our earlier examples in the Timelines to set up movement of a randomly chosen object, adding a second <TimedAction> to move a randomly chosen object backwards and adjusting durations and delays accordingly.

``<TimelineRoot>``

    ``<Timeline name=“Looping Timeline” start-immediately=“true”>``

        ``<TimedActions seconds-time= “0.5”>``

            ``<GroupRef name= “MyGroup” random= “Select One Randomly”>``

                ``<Transition duration= “1.0”>``

                    ``<MoveRel>``
					
                        ``<Placement>``
						
                            ``<RelativeTo>Center</RelativeTo>``
							
                            ``<Position>(0,0,2)</Position>``
					
                        ``</Placement>``

                    ``</MoveRel>``

                ``</Transition>``

            ``</GroupRef>``

        ``</TimedActions>``    

        ``<TimedActions seconds-time= “1.5”>``

            ``<GroupRef name= “MyGroup” random= “Select One Randomly”>``

                ``<Transition duration= “1.0”>``

                    ``<MoveRel>``
					
                        ``<Placement>``
						
                            ``<RelativeTo>Center</RelativeTo>``
							
                            ``<Position>(0,0,-2)</Position>``
					
                        ``</Placement>``
				
                    ``</MoveRel>``
			
                ``</Transition>``
		
            ``</GroupRef>``
	
        ``</TimedActions>``

        ``<TimedActions seconds-time=”2.5”>``
			
            ``<TimerChange name = “Looping Timeline”>``
				
                ``<start/>``
			
            ``</TimerChange>``

        ``</TimedActions>``
	
    ``</Timeline>``

``<TimelineRoot>``

And that’s all it takes! We just add the path and ``<Story>`` tags to the beginning, and the ``<Global>`` and ``<PlacementRoot>`` information to the end, and we’ve already got ourselves a working project! What comes next is innumerable in possibilities, and—even better—completely up to you!