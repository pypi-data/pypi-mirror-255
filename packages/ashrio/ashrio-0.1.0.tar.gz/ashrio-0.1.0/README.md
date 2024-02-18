# Ashrio
_A frontend web-framework made in python, for python, with python in mind constantly_

Ashrio is the thing I've been looking for but could never find: a frontend-web framework in python that is easy to use ***and even easier to extend****. Right now it is JUST starting out, there are a grand total of 4 components, 5 if you count the grid system. It is simple and probably not useable at the moment, but hopefully it will be. 

## The Idea + How to customize
I wanted something I could EXTEND easily. To extend this, you only really need your class to be a subclass of pydantic BaseModel, to have a filepath parameter, and to define a get_html method and a recommended write_to_file method (which is basically 3 lines of code once youve defined the get_html method haha). 

The get_html method should do the following:
- take the "props" (pydantic items) and integrate them into the styles/content/whatever they do
- output html with styles, js, or whatever you want
  i. the only rule about the html is that it needs a style_extra parameter with a default set to "" that plugs into (usually) the top level div/whatever. This is how the grid system works, so it is a must

there is a write_to_file method defined in utils that handles the complex stuff, so really you just need to get the code from get_html and then use the write_to_file method.

If you have any questions, PLEASE ask.

## Plans/Future
- Move to react (not sure if this is even worth it, might make it harder to use..
- Add more styling options
- add a ton more components
- add an event handling system
- migrate to tailwind
- use Alpine for reactivity and better functionality (WIP)


