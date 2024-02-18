import mystring, asyncio, threading

from pnostic.structure import Envelop, RepoResultObject, RepoObject, RepoSifting, Runner
from pnostic.utils import now

class app(Envelop):
    """
    https://www.pyvibe.com/flask.html

    https://github.com/pycob/pyvibe

    https://stackoverflow.com/questions/31264826/start-a-flask-application-in-separate-thread

    https://www.pyvibe.com/gallery/chart.html
    """
    def __init__(self, ipaddress:str="127.0.0.1", port_to_use:int=5000):
        super().__init__()
        self.imports = [
            "pyvibe",
            "flask",
            "plotly"
        ]
        self.flask_app = None
        self.flask_runner_thread = None
        self.host = ipaddress
        self.port = port_to_use

    def initialize(self)->bool:
        self.flask_runner_thread = threading.Thread(target=self.flask_runner, args=(), daemon = True)
        self.flask_runner_thread.start()
        return True

    def name(self) -> mystring.string:
        return mystring.string.of("LiveGraph")

    def flask_runner(self):
        self.installImports()
        from flask import Flask
        import pyvibe as pv
        self.flask_app = Flask(__name__)

        @self.flask_app.route("/")
        def index():
            page = pv.Page('Home')
            page.add_header('Hello World')
            with page.add_card() as card:
                card.add_header("Load the graph")
                card.add_link("Learn more", "http://{0}:{1}/graph".format(self.host, self.port))
            return page.to_html()

        @self.flask_app.route("/graph")
        def graph():
            """
            https://www.pyvibe.com/gallery/chart.html
            """
            import pyvibe as pv
            from pyvibe import HtmlComponent as html
            import plotly.express as px

            df = mystring.frame.from_arr([{
                "Runner": "Cryptolation",
                "NumberProjects": 10 
            }, {
                "Runner": "Semgrep",
                "NumberProjects": 4 
            }])

            #https://stackoverflow.com/questions/31638439/remove-highlight-from-active-button

            page = pv.Page("Number of Repo Objects Scanned")
            page.add_header("Chart")


            page.add_html("""
<style>
.mystyle {
  width: 100%;
  padding: 25px;
  background-color: coral;
  color: white;
  font-size: 25px;
  box-sizing: border-box;
}
</style>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>
<script>
     var time = new Date().getTime();
     $(document.body).bind("mousemove keypress", function(e) {
         time = new Date().getTime();
     });

     function refresh() {
         if(new Date().getTime() - time >= 60000 && document.getElementById("myDIV").innerHTML != "Stopped Reloading") 
             window.location.reload(true);
         else 
             setTimeout(refresh, 10000);
     }

     setTimeout(refresh, 10000);
</script>

<script>
function myFunction() {
   var element = document.getElementById("myDIV");
   element.classList.toggle("mystyle");
   if (element.innerHTML == "") {
    element.innerHTML = "Stopped Reloading";
   } else {
    element.innerHTML = "";
   }
}
</script>
<button onclick="myFunction()">Start refreshing</button>
<div id="myDIV"></div>
""")

            fig = px.bar(df, x='Runner', y='NumberProjects')
            page.add_plotlyfigure(fig)

            return page.to_html()
        
        self.flask_app.run(host=self.host, port=self.port, debug=True,use_reloader=False)

    def clean(self) -> bool:
        return True

    def per_next_repo_obj(self,repo_object: RepoObject):
        return

    def per_repo_obj_scan(self,repo_object: RepoObject, runner:Runner):
        return

    def per_repo_obj_scan_result(self,repo_object: RepoResultObject, runner:Runner):
        return