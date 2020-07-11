from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox 
from kivy.uix.behaviors import CompoundSelectionBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.app import runTouchApp
from kivy.clock import Clock
from kivy.factory import Factory

from OBS_MANAGER import OBS_MANAGER,getSceneName

class SelectableGrid(FocusBehavior, CompoundSelectionBehavior, GridLayout):

    def __init__(self, **kwargs):
        super(SelectableGrid, self).__init__(**kwargs)

        def print_selection(*l):
            print('selected: ', [x.text for x in self.selected_nodes])
        self.bind(selected_nodes=print_selection)

        self.m = OBS_MANAGER()
        self.m.getScenes()

        self.param = {}
        self.param["slider1"] = {}

        Clock.schedule_interval(self.update, 0.01)

    def select_node(self, node):
        node.background_color = (1, 0, 0, 1)
        return super(SelectableGrid, self).select_node(node)

    def deselect_node(self, node):
        node.background_color = (1, 1, 1, 1)
        super(SelectableGrid, self).deselect_node(node)

    def do_touch_menu(self, instance, touch):
        if ('button' in touch.profile and touch.button in
                ('scrollup', 'scrolldown', 'scrollleft', 'scrollright')) or\
                instance.collide_point(*touch.pos):
            if instance.type=="top":
                if instance.text == "reset":
                    print("reset button")
                    self.m.getScenes()
        else:
            return False
        return True

    def do_touch(self, instance, touch):
        if ('button' in touch.profile and touch.button in
                ('scrollup', 'scrolldown', 'scrollleft', 'scrollright')) or\
                instance.collide_point(*touch.pos):
            self.select_with_touch(instance, touch)
            if instance.type=="scene":
                self.m.switchScene(instance.scene)
            if instance.type=="move":
                if instance.scene in self.param["slider1"].keys():
                    self.m.updateScene(instance.scene,instance.idx,speed = self.param["slider1"][instance.scene])
                else:
                    self.m.updateScene(instance.scene,instance.idx)
        else:
            return False
        return True

    def OnSliderValueChange(self,instance,value):
        print("value",int(value))
        self.param["slider1"][instance.scene] = int(value)

    def update(self,dt):
        self.m.update()
        return

def main():
    scene_num = 4
    col_width = scene_num + 3
    root = SelectableGrid(cols=col_width, up_count=5, multiselect=True, scroll_count=1)
    print("-------------------------")
    print(root.m.keyScenes)
    print("-------------------------")
    topCommand=[
        ["reset"],
        ["c0"],
        ["c1"],
        ["c2"],
        ["c3"],
        ["c4"],
        ["c5"]
        ]
    for i in range(col_width):
        c = Button(text=topCommand[i][0])
        c.type = "top"
        c.bind(on_touch_down=root.do_touch_menu)
        root.add_widget(c)
        
    for i in root.m.keyScenes:
        c = Button(text=i)
        c.type = "scene"
        c.scene = i
        c.bind(on_touch_down=root.do_touch)
        root.add_widget(c)
        for j in range(1,1+scene_num):
            c = Button(text=getSceneName(i,j))
            c.type = "move"
            c.scene = i
            c.idx = j
            c.bind(on_touch_down=root.do_touch)
            root.add_widget(c)

        c = Factory.Slider(value=30, min=10, max=50, size_hint_y=.3)
        c.scene = i
        c.bind(value=root.OnSliderValueChange)
        root.add_widget(c)

        c = CheckBox()
        c.type = "check"
        c.scene = i
        #c.bind(on_touch_down=root.do_touch)
        root.add_widget(c)

    runTouchApp(root)

if __name__ == "__main__":
    main()


