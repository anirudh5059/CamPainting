import cv2
import mediapipe as mp
import numpy as np
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


brushThickness = 3
drawColor = (0, 0, 128)

# For static images:
IMAGE_FILES = []
with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5) as hands:
  for idx, file in enumerate(IMAGE_FILES):
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    image = cv2.flip(cv2.imread(file), 1)
    # Convert the BGR image to RGB before processing.
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Print handedness and draw hand landmarks on the image.
    print('Handedness:', results.multi_handedness)
    if not results.multi_hand_landmarks:
      continue
    image_height, image_width, _ = image.shape
    annotated_image = image.copy()
    for hand_landmarks in results.multi_hand_landmarks:
      print('hand_landmarks:', hand_landmarks)
      print(
          f'Index finger tip coordinates: (',
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width}, '
          f'{hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height})'
      )
      mp_drawing.draw_landmarks(
          annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    cv2.imwrite(
        '/tmp/annotated_image' + str(idx) + '.png', cv2.flip(annotated_image, 1))

def check_dist(x1, y1, x2, y2):
  dist = np.linalg.norm([x1-y1, x2-y2])
  if(dist > 600):
    return False
  else:
    return True

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  prev_list = -1*np.ones((2,50), dtype = np.uint8)
  draw_flag = False
  success, image = cap.read()
  image_height, image_width, _ = image.shape
  slate = np.zeros((image_height,image_width,3), np.uint8)
  while cap.isOpened():
    success, image = cap.read()
    image_height, image_width, _ = image.shape
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue
    # Flip the image horizontally for a later selfie-view display, and convert
    # the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
#print(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width)
#print(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height)
        x1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width)
        y1 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height)
        if(x1 >= image_width):
          x1 = image_width - 1
        if(y1 >= image_width):
          x1 = image_height - 1
        if(draw_flag):
          cv2.circle(slate, (x1, y1), int(brushThickness/2), drawColor, cv2.FILLED)
          if(prev_list[0,0] != -1 and prev_list[1,0] != -1
              and check_dist(prev_list[0,0], prev_list[1,0], x1, y1)):
            cv2.line(slate, (prev_list[0,0], prev_list[1,0]), (x1, y1), drawColor, brushThickness)
          for i in range(prev_list.shape[1]-1):
            if(prev_list[0,i] != -1 and prev_list[1,i] != -1
                and prev_list[0,i+1] != -1 and prev_list[1,i+1] != -1
                and check_dist(prev_list[0,i+1], prev_list[1,i+1], prev_list[0,i], prev_list[1,i])):
              cv2.line(slate, (prev_list[0,i+1], prev_list[1,i+1]), (prev_list[0,i], prev_list[1,i]), drawColor, brushThickness)

        prev_list[:,1:] = prev_list[:,:-1]
        prev_list[0,0] = x1
        prev_list[1,0] = y1
        #mp_drawing.draw_landmarks(
        #    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    out = cv2.add(image, slate)
    cv2.imshow('MediaPipe Hands', out)
    bset = cv2.waitKey(1)
    if bset & 0xFF == ord('d'):
      draw_flag = not draw_flag
      prev_list = -1*np.ones((2,25), dtype = np.uint8)
    elif bset & 0xFF == ord('e'):
      slate = np.zeros((image_height,image_width,3), np.uint8)
    elif bset & 0xFF == ord('q'):
      break
cap.release()

