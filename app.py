from gekko import GEKKO
from pywebio.input import input, input_group
from pywebio.output import put_text, put_table, use_scope, put_button
import numpy as np

def main():
    with use_scope('process', clear=True):
        m = GEKKO(remote=False)
        
        #Define solo missions
        mission_types = ["Follower","Spell","Card_to_draw","Evolution"]
        
        prompt = "Enter your target numbers for the solo missions (If not applicable, type 0):"
        
        #Tick your solo missions
        data = input_group(prompt,
                           [input(t, type="number", value=0,name=t,required=True) for t in mission_types]
                           )
        
        # Calculate the target numbers
        flw = int(data["Follower"])
        spl = int(data["Spell"])
        cd = int(data["Card_to_draw"])
        evo = int(data["Evolution"])
        
        classes = ["Forest/エルフ", 
                   "Sword/ロイヤル", 
                   "Rune/ウイッチ", 
                   "Dragon/ドラゴン", 
                   "Shadow/ネクロ", 
                   "Blood/ヴァンプ", 
                   "Haven/ビショップ", 
                   "Portal/ネメシス"]
        flw_coef = [4,2,1,2,2,2,1,3]
        spl_coef = [1,0,3,1,1,1,1,0]
        cd_coef = [3,2,3,3,3,2,3,3]
        evo_coef = [1,0,1,2,0,0,1,1]
        
        #initialize variables
        x = m.Array(m.Var,8,value=0,lb=0,ub=30, integer=True)
        
        #Equations
        m.Equation(x @ flw_coef >= flw)
        m.Equation(x @ spl_coef >= spl) 
        m.Equation(x @ cd_coef >= cd) 
        m.Equation(x @ evo_coef >= evo)
        
        # objective
        m.Minimize(np.sum(x))
        
        m.options.SOLVER=1
        m.solve(disp=False)

    with use_scope('result', clear=True):
        txt = "Your solo missions:\n{0} followers\n{1} spells\n{2} cards to draw\n{3} evolutions".format(flw,spl,cd,evo)
        put_text(txt)
        put_table([[c, int(n[0]), f, s, cd, e] for c, n, f, s, cd, e in zip(classes, x, flw_coef, spl_coef, cd_coef, evo_coef)],
                  header=["Class", "Times of tutorial", "Followers per time", "Spells per time","Cards per time","Evos per time"])
        put_button("Back", onclick=lambda: main())
        
if __name__ == '__main__':
    import argparse
    from pywebio.platform.tornado_http import start_server as start_http_server
    from pywebio import start_server as start_ws_server

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("--http", action="store_true", default=False, help='Whether to enable http protocol for communicates')
    args = parser.parse_args()

    if args.http:
        start_http_server(main, port=args.port)
    else:
        # Since some cloud server may close idle connections (such as heroku),
        # use `websocket_ping_interval` to  keep the connection alive
        start_ws_server(main, port=args.port, websocket_ping_interval=30)
