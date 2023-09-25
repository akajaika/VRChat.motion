import cv2
import mediapipe as mp
import tkinter as tk

import argparse
from pythonosc import udp_client

import win32api
import win32con

# 初期座標を指定
WRIST_x = 300
WRIST_y = 200
INDEX_FINGER_TIP_y = 200
MIDDLE_FINGER_TIP_y = 200
RING_FINGER_TIP_y = 200
PINKY_FINGER_TIP_y = 200
INDEX_FINGER_TIP_x = 200
MIDDLE_FINGER_TIP_x = 200
RING_FINGER_TIP_x = 200
PINKY_FINGER_TIP_x = 200
INDEX_FINGER_MCP_y = 300
INDEX_FINGER_MCP_x = 300
MIDDLE_FINGER_MCP_x = 300
RING_FINGER_MCP_x = 300
PINKY_FINGER_MCP_x = 300
fx = 300*3.2
fy = 200*2.7


# Webカメラから入力
cap = cv2.VideoCapture(0)

# Tkクラス生成
frm = tk.Tk()
# 画面サイズ
frm.geometry('1920x1080')
# 画面タイトル
frm.title('handmodel')

# Canvasウィジェットをウィンドウに配置
canvas = tk.Canvas(frm, width=1920, height=1080)
canvas.pack()

# Handモデルのインスタンス化
with mp.solutions.hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

# ウィンドウに円を描画
    circle_center_x = 300 * 3.2
    circle_center_y = 200 * 2.7
    circle_radius = 50
    canvas.delete("all")  # 既存の描画を消去
    canvas.create_oval(circle_center_x - circle_radius, circle_center_y - circle_radius,
                        circle_center_x + circle_radius, circle_center_y + circle_radius, fill='red')

    #VRChat用のスクリプト
    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default="127.0.0.1",
            help="The ip of the OSC server")
        parser.add_argument("--port", type=int, default=9000,
            help="The port the OSC server is listening on")
        args = parser.parse_args()

        client = udp_client.SimpleUDPClient(args.ip, args.port)

    # ウィンドウ表示の無限ループ
    while True:
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 手の位置検出と描画
        results = hands.process(image)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for index, landmark in enumerate(hand_landmarks.landmark):
                    # 関節の座標を取得
                    x, y = int(landmark.x * image.shape[1]), int(landmark.y * image.shape[0])

                    # 各指の先の位置を取得
                    if index == 8:  # インデックス指の先
                        INDEX_FINGER_TIP_y = y
                    elif index == 12:  # 中指の先
                        MIDDLE_FINGER_TIP_y = y
                    elif index == 16:  # 薬指の先
                        RING_FINGER_TIP_y = y
                    elif index == 20:  # 小指の先
                        PINKY_FINGER_TIP_y = y
                    elif index == 5:  # 中指の先
                        INDEX_FINGER_MCP_y = y
                        INDEX_FINGER_MCP_x = x
                    elif index == 9:  # 薬指の先
                        MIDDLE_FINGER_MCP_x = x
                    elif index == 13:  # 小指の先
                        RING_FINGER_MCP_x = x
                    elif index == 17:  # 小指の先
                        PINKY_FINGER_MCP_x = x
                    elif index == 4:  
                        THUMB_FINGER_TIP_x = x
                    elif index == 4:  
                        THUMB_FINGER_TIP_y = y

                    print(f"Hand {results.multi_handedness[0].classification[0].label}: Joint {index} - X: {x}, Y: {y}")

                # 検出された手の骨格をカメラ画像に重ねて描画
                mp.solutions.drawing_utils.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp.solutions.hands.HAND_CONNECTIONS)
        


        # カメラ画像を表示
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))

        # 手首の座標を取得して、WRIST_xとWRIST_yを更新
        if results.multi_hand_landmarks:
            wrist_landmark = results.multi_hand_landmarks[0].landmark[0]  # 手首に対応する最初のランドマークを仮定
            WRIST_x, WRIST_y = int(wrist_landmark.x * image.shape[1]), int(wrist_landmark.y * image.shape[0])


        
            #視点移動　水平     
            if WRIST_x > 400:
                key_input = -0.2
                client.send_message("/input/LookHorizontal", key_input)

            if WRIST_x < 200:
                key_input = 0.2
                client.send_message("/input/LookHorizontal", key_input)
            
            if 200 < WRIST_x < 400:
                key_input = 0.1
                client.send_message("/input/LookHorizontal", key_input)

            #視点移動　垂直
            if  WRIST_y > 250:
                key_input = -0.2
                client.send_message("/input/LookVertical", key_input)

            if  WRIST_y < 300:
                key_input = 0.2
                client.send_message("/input/LookVertical", key_input)

            if  250 < WRIST_y < 400:
                key_input = 0.1
                client.send_message("/input/LookVertical", key_input)
            



        # 手首と指の位置の差の条件を設定して握りこみの判定
        if  (INDEX_FINGER_MCP_y < INDEX_FINGER_TIP_y) and (INDEX_FINGER_MCP_y < MIDDLE_FINGER_TIP_y) and (INDEX_FINGER_MCP_y < RING_FINGER_TIP_y)  and (INDEX_FINGER_MCP_y < PINKY_FINGER_TIP_y) :
                circle_center_x = circle_center_x + (WRIST_x * 3.2 - fx)
                circle_center_y = circle_center_y + ((WRIST_y - 200) * 2.7 - fy)
                circle_radius = 50
                
                #左クリック　押す
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

                fx = WRIST_x * 3.2
                fy = (WRIST_y - 200) * 2.7
                canvas.delete("all")  # 既存の描画を消去 これ消したら残像で絵が描ける
                canvas.create_oval(circle_center_x - circle_radius, circle_center_y - circle_radius,
                        circle_center_x + circle_radius, circle_center_y + circle_radius, fill='blue')
                
                
                
        else: 
                #左クリック　離す
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                fx = WRIST_x * 3.2
                fy = (WRIST_y - 200) * 2.7
                
                
               

        




        # ウィンドウをアップデート
        frm.update()

        # Escキーで終了
        if cv2.waitKey(5) & 0xFF == 27:
            break

# HandモデルとWebカメラの解放とOpenCVウィンドウの破棄
cap.release()
cv2.destroyAllWindows()

# Tkinterウィンドウの表示を維持
frm.mainloop()