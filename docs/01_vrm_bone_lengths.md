# **A Data-Driven Framework for Realistic VRM Avatar Proportions Based on Japanese Anthropometric Data**

## **The VRM 1.0 Humanoid Skeleton: A Technical Primer**

To establish a robust, data-driven framework for avatar proportions, one must first build upon a solid technical foundation. In the landscape of cross-platform virtual reality (VR) and augmented reality (AR) applications, the VRM format has emerged as a critical standard for ensuring avatar interoperability. This section provides a detailed technical analysis of the VRM 1.0 humanoid specification, defining the precise skeletal structure, coordinate system, and binding pose that serve as the non-negotiable constraints for all subsequent anthropometric calculations. A thorough understanding of these specifications is not merely procedural; it is fundamental to producing a final model that is compliant, functional, and compatible across the wide ecosystem of VRM-enabled platforms.

### **1.1 The VRM Standard and its Design Philosophy**

VRM is a platform-independent, open file format meticulously designed for the handling of 3D humanoid avatar data, primarily within the context of VR applications and the broader metaverse.1 It is not a format created from scratch, but rather an intelligent extension of the glTF 2.0 standard, a highly efficient, royalty-free specification for the transmission and loading of 3D scenes and models. By building upon glTF, VRM inherits its robust capabilities for handling geometry, materials, and textures within a single, compact file, which is a significant advantage for runtime loading in interactive applications.3

The core design philosophy of VRM is to solve the pervasive problem of avatar incompatibility. Historically, 3D model data formats have been highly variable, with no consistent bone structure, coordinate system, or scale.3 This fragmentation required developers to implement custom logic and motion retargeting for each individual character model, a time-consuming and often imperfect process. VRM addresses this by imposing a set of strict, well-defined standards that guarantee a baseline of compatibility. These standards dictate not only the 3D model data but also crucial information for "use as an avatar," such as standardized facial expressions (blend shapes), gaze control (look at), and physics for secondary motion (spring bones).2

Central to this standardization are the constraints on the model's coordinate system and units. The VRM specification mandates a right-handed, Y-Up coordinate system, which aligns with the conventions of major 3D engines like Unity. Furthermore, it standardizes units to the metric system, where one unit in the model's space is equivalent to one meter in the virtual world.1 This seemingly simple rule is profoundly important; it eliminates the ambiguity of scale that plagues many other formats, ensuring that an avatar created in one application will appear at the correct physical size in another without manual rescaling. This consistency is paramount for creating immersive and believable social VR experiences where user avatars must interact with each other and the environment at a plausible human scale.

### **1.2 The Official VRM 1.0 Humanoid Bone Hierarchy**

The cornerstone of the VRM standard's interoperability is its definition of a mandatory humanoid bone hierarchy. This is not a set of recommendations but a rigid specification that a 3D model's skeleton must adhere to in order to be classified as a valid VRM humanoid. This standardized skeleton ensures that animations, motion capture data, and inverse kinematics (IK) solutions can be applied universally to any compliant avatar, regardless of its unique aesthetic or proportions.4 The specification, detailed in the humanoid field of the VRMC_vrm extension, maps specific functional roles to nodes within the glTF scene graph.5

The hierarchy is divided into required, conditionally required, and optional bones, each with a fixed parent-child relationship.

**Required Bones:** These form the absolute minimum skeleton necessary for basic humanoid motion. The absence of any of these bones would render the avatar non-compliant. The required bones are 5:

- **Torso:** hips, spine
- **Head:** head
- **Arms:** leftUpperArm, leftLowerArm, leftHand, rightUpperArm, rightLowerArm, rightHand
- **Legs:** leftUpperLeg, leftLowerLeg, leftFoot, rightUpperLeg, rightLowerLeg, rightFoot

**Conditionally Required and Essential Bones:** While the VRM 1.0 specification has slightly different language than its 0.x predecessor, certain bones are functionally essential for a recognizable and animatable humanoid torso. The chest and neck bones, which were explicitly required in VRM 0.x, remain critical links in the skeletal chain. The chest bone must be a child of the spine, and the neck bone's parent is typically the upperChest or, if absent, the chest.5 For the purposes of creating a functional, high-quality avatar, these should be considered de facto requirements.

**Optional Bones:** These bones add greater fidelity and expressiveness to the avatar but are not strictly necessary for basic compliance. They include 5:

- upperChest
- leftShoulder, rightShoulder
- leftToes, rightToes
- leftEye, rightEye, jaw
- All finger bones (e.g., leftThumbProximal, leftIndexIntermediate, etc.)

The parent-child relationship is immutable. For example, spine must always be a child of hips, chest must be a child of spine, and leftUpperLeg must be a child of hips. This creates a predictable kinematic chain from the root of the character (hips) to all extremities. It is permissible to have non-humanoid bones between the specified humanoid bones (e.g., a "twist" bone in the forearm between leftUpperArm and leftLowerArm), but the direct hierarchical lineage of the required bones must be preserved.5

The following diagram illustrates the fundamental parent-child structure of the VRM 1.0 humanoid skeleton:

```
root (origin)
└── hips
    ├── spine
    │   └── chest
    │       └── (upperChest)
    │           └── neck
    │               └── head
    │                   ├── (leftEye)
    │                   ├── (rightEye)
    │                   └── (jaw)
    ├── leftUpperLeg
    │   └── leftLowerLeg
    │       └── leftFoot
    │           └── (leftToes)
    ├── rightUpperLeg
    │   └── rightLowerLeg
    │       └── rightFoot
    │           └── (rightToes)
    └── (leftShoulder)
        └── leftUpperArm
            └── leftLowerArm
                └── leftHand
                    └── (fingers)...
    └── (rightShoulder)
        └── rightUpperArm
            └── rightLowerArm
                └── rightHand
                    └── (fingers)...
```

### **1.3 The T-Pose Mandate and Its Implications**

A critical technical requirement of the VRM standard is that all humanoid models must be defined in a specific "T-Pose" as their rest, or bind, pose.3 This pose is characterized by the figure standing upright along the Y-axis, with arms extended straight out parallel to the X-axis and palms facing downwards. In VRM 1.0, the character must be facing forward along the positive Z-axis.3

This mandate is not an arbitrary artistic choice; it is a cornerstone of the format's technical design. The T-Pose establishes a universal, neutral, and mathematically simple starting point for all skeletal transformations. In modern animation systems, motion data is not stored as absolute world positions for each bone in every frame. Instead, it is stored as a series of rotations relative to a predefined rest pose.7 By standardizing this rest pose to the T-Pose, VRM ensures that a single animation file can be applied to any compliant avatar and produce the same intended motion. If one avatar were bound in an A-Pose and another in a T-Pose, applying the same animation data—for example, an instruction to rotate the

leftUpperArm bone by 45 degrees—would result in two visually distinct and incorrect poses.

This has a direct and profound implication for the work of this report. The bone lengths calculated herein are defined as the vector distance between the pivot point of a parent bone and the pivot point of its child bone _while the skeleton is in the specified T-Pose_. For example, the length of the leftUpperArm is the distance from the leftShoulder (or upperChest) joint to the leftLowerArm (elbow) joint. This measurement is only valid and meaningful within the context of the T-Pose. Any deviation from this standard during the initial modeling and rigging phase would render the anthropometrically derived proportions inaccurate, as the distances between joints would change. Therefore, the T-Pose mandate is the fundamental geometric assumption upon which this entire data-driven framework is built.

## **Reference Anthropometry of the Young-Adult Japanese Population**

Having established the technical specifications of the target VRM skeleton, the next critical step is to source high-quality, relevant anthropometric data to serve as the ground truth for our proportional model. The user query specifically requests data for young-adult Japanese men and women (ages 20-39). The selection of this data is the most important factor influencing the final accuracy and applicability of the results. This section details the process of selecting an appropriate data source, justifies the choice made, and presents the key measurements that will drive the subsequent calculations.

### **2.1 Data Source Selection and Justification**

The ideal data source for this project must be both authoritative and granular. It must come from a reliable, official body and contain not just high-level measurements like stature and weight, but detailed segmental measurements corresponding to the major limbs and torso.

Two primary official sources for Japanese anthropometric data were considered:

1. **Japan's National Health and Nutrition Survey (NHNS):** This is an annual, nationwide survey conducted by the Ministry of Health, Labour and Welfare (MHLW) and is the most current source of data on the Japanese population.8 The most recent comprehensive report available is for the year 2019\.10 However, a review of the publicly available summaries and documentation for the NHNS reveals that its focus is primarily on public health indicators. The physical examination section details the collection of height, body weight, abdominal circumference, blood pressure, and blood test results.10 While invaluable for health policy, it lacks the specific segmental measurements required for skeletal construction, such as crotch height (inseam), acromial height (shoulder height), or dactylion height (fingertip height).10
2. **AIST Human Dimension Database (1991–92):** The National Institute of Advanced Industrial Science and Technology (AIST), a major Japanese research institution, maintains a highly detailed anthropometric database compiled from a survey conducted in 1991 and 1992\.12 This survey was specifically designed for industrial and ergonomic applications and, as such, contains a comprehensive list of 251 measurements for males and 254 for females.13 Crucially, this list includes the exact measurements needed to derive primary body segments: stature, crotch height, cervicale height, acromial height, and dactylion height.13

The choice between these two sources presents a classic trade-off between data recency and data granularity. While the NHNS 2019 data is three decades more current, it is functionally insufficient for the task of calculating individual bone lengths. The AIST 1991-92 database, though older, provides the exact, high-quality measurements necessary to fulfill the technical requirements of this report.

Therefore, the decision was made to proceed using the AIST 1991-92 database. This choice is made with the explicit acknowledgment of its primary limitation: the age of the data. It is well-documented that secular trends in nutrition and lifestyle can lead to changes in average population anthropometry over time.15 For instance, studies on Korean and Japanese populations have shown a gradual increase in average stature over the past several decades.16 The results generated in this report will thus represent a statistically accurate model of the young-adult Japanese population of the early 1990s. While more recent granular data would be ideal, the AIST database remains the most suitable and comprehensive public resource for this specific type of analysis. This approach prioritizes methodological soundness and completeness, providing a robust baseline that can be updated in the future should a more recent, equally detailed dataset become available.

### **2.2 Key Anthropometric Measurements (AIST 1991-92, 18-29 Age Group)**

The following data points were extracted from the AIST Human Dimension Database 1991-92 for the "Younger Group" cohort, which comprises individuals aged 18 to 29\. These values represent the foundational measurements from which all VRM bone lengths will be derived. All measurements are presented in meters, converted from the original millimeters, to align with the VRM standard. The mean serves as the basis for the median avatar, while the standard deviation is essential for defining the realistic range of variation for the UI customization controls discussed in Section 5\.

| Measurement        | AIST ID | Male Mean (m) | Male SD (m) | Female Mean (m) | Female SD (m) |
| :----------------- | :------ | :------------ | :---------- | :-------------- | :------------ |
| Stature            | B1      | 1.714         | 0.055       | 1.594           | 0.049         |
| Crotch Height      | B18     | 0.800         | 0.039       | 0.736           | 0.035         |
| Cervicale Height   | B8      | 1.452         | 0.052       | 1.350           | 0.047         |
| Acromial Height    | B19     | 1.407         | 0.052       | 1.308           | 0.046         |
| Dactylion Height   | B22     | 0.652         | 0.038       | 0.606           | 0.034         |
| Biacromial Breadth | C1      | 0.390         | 0.018       | 0.356           | 0.016         |

Data sourced from the AIST Human Dimension Database 1991-92, targeting the 18-29 age group.13

## **Methodology: Translating Anthropometry to a Digital Skeleton**

The process of converting external, surface-level anthropometric measurements into the internal bone lengths of a digital skeleton is a multi-step procedure that requires a combination of direct calculation and the application of established anatomical and forensic ratios. This section outlines a transparent and repeatable methodology for this translation. The process is divided into two primary stages: first, the derivation of major body segments from the raw AIST data, and second, the subdivision of these segments into the specific bone lengths required by the VRM 1.0 humanoid hierarchy.

### **3.1 Step 1: Derivation of Primary Body Segments from AIST Data**

The initial step involves transforming the landmark-based height measurements from the AIST database into functionally distinct body segments. These segments represent the total lengths of the torso, legs, and arms, which will subsequently be divided into their constituent bones.

- **Total Leg Length (Inseam):** This is the most direct measurement, corresponding to the AIST Crotch Height (股下高). It represents the distance from the perineum to the floor.
  - Male: 0.800 m
  - Female: 0.736 m
- **Torso Length:** This segment represents the length of the vertebral column from the base of the neck to the pelvis. It is calculated as the difference between Cervicale Height (頸椎点高), the height of the 7th cervical vertebra, and Crotch Height.
  - Male: 1.452 m−0.800 m=0.652 m
  - Female: 1.350 m−0.736 m=0.614 m
- **Total Arm Length:** This is the full length of the arm from the shoulder to the fingertips. It is calculated as the difference between Acromial Height (肩峰高), the height of the acromion process on the shoulder, and Dactylion Height (指先高), the height of the tip of the middle finger.
  - Male: 1.407 m−0.652 m=0.755 m
  - Female: 1.308 m−0.606 m=0.702 m
- **Head and Neck Segment:** This combined segment represents the total length from the top of the head to the base of the neck (C7 vertebra). It is calculated as the difference between total Stature (身長) and Cervicale Height.
  - Male: 1.714 m−1.452 m=0.262 m
  - Female: 1.594 m−1.350 m=0.244 m
- **Foot Height:** The VRM hierarchy includes a foot bone, but the lowerLeg bone terminates at the ankle. To accurately calculate the length of the lowerLeg (tibia), the height of the foot (from the ankle joint to the floor) must be subtracted from the total leg length. As this was not directly measured in the AIST survey, it is estimated using a standard anthropometric proportion. Foot height is approximately 3.7% of total stature.
  - Male: 1.714 m×0.037=0.063 m
  - Female: 1.594 m×0.037=0.059 m

### **3.2 Step 2: Subdivision of Primary Segments into VRM Bone Lengths**

With the primary segments defined, the next step is to subdivide them into the individual bone lengths required by the VRM skeleton. This process relies on proportional ratios derived from anatomical studies, artistic anatomy canons, and forensic science, which provide established relationships between the lengths of different bones within a limb or body segment.

#### **3.2.1 Legs (upperLeg, lowerLeg)**

The total leg length must be divided between the femur (upperLeg) and the tibia (lowerLeg). The relationship between these two bones is described by the Tibia:Femur Ratio (TFR), also known as the crural index.18 Studies of skeletally mature individuals have established a normative mean TFR of approximately 0.78 to 0.80.18 A study focusing specifically on Japanese endurance runners found a slightly higher mean ratio of 0.84.20 To balance these findings for a general young-adult Japanese population, this methodology adopts a

**TFR of 0.83**.

First, the effective leg length for the bones is determined by subtracting the estimated foot height from the total leg length (inseam). Let this be Lleg​.

Lleg​=Total Leg Length−Foot Height

The lengths of the upperLeg and lowerLeg are then calculated as follows:

LupperLeg​=1+RTFR​Lleg​​=1.83Lleg​​

LlowerLeg​=LupperLeg​×RTFR​=LupperLeg​×0.83

#### **3.2.2 Arms (upperArm, lowerArm)**

The total arm length must be divided between the humerus (upperArm) and the radius/ulna (lowerArm). This requires first accounting for the length of the hand, which is part of the Total Arm Length measurement but is represented by a separate hand bone in VRM. A widely used proportion in both artistic and scientific anatomy is that hand length is approximately equal to face height, which corresponds to roughly 1/10th of total stature.21

Let Larm​ be the length of the arm bones after subtracting the estimated hand length.

Larm​=Total Arm Length−(Stature/10)

For subdividing Larm​, the work of Dr. Paul Richer in "Artistic Anatomy" provides a robust and practical guide. Richer's analysis of human proportions indicates that the length of the upper arm (from the acromion to the epicondyles of the humerus) is approximately equal to the length of the forearm (from the epicondyles to the knuckles).22 This establishes a simple and anatomically sound

**1:1 ratio** between the upperArm and lowerArm bones.

LupperArm​=2Larm​​

LlowerArm​=2Larm​​

#### **3.2.3 Torso (spine, chest, upperChest) and Head/Neck (neck, head)**

Subdividing the torso and neck is the most complex part of this process, as direct anthropometric data for individual vertebral segments is not available. An estimation model based on anatomical proportions is therefore necessary. The VRM hierarchy for the torso consists of spine, chest, and (optionally but recommended) upperChest, which correspond roughly to the lumbar, lower-to-mid thoracic, and upper thoracic regions of the vertebral column, respectively. The neck bone corresponds to the cervical spine.

The calculated Torso Length (0.652 m for males, 0.614 m for females) represents the combined length of the lumbar and thoracic spine. The Head and Neck Segment (0.262 m for males, 0.244 m for females) represents the combined length of the cervical spine and the cranium.

To partition these segments, the following proportional model is applied:

1. Torso Partition: The Torso Length is allocated to the spine, chest, and upperChest bones. In the absence of more detailed data, and to create a balanced and flexible rig, this length is distributed equally among the three segments. This provides a functional approximation of the lumbar and thoracic vertebral sections.  
   Lspine​=Lchest​=LupperChest​=3Torso Length​
2. Head/Neck Partition: The Head and Neck Segment is partitioned between the neck and head bones. Anatomically, the cervical spine (neck) constitutes a significant portion of this total length. A ratio of 40% for the neck and 60% for the head is used to reflect this relationship.  
   Lneck​=Head and Neck Segment×0.40  
   Lhead​=Head and Neck Segment×0.60

This methodology, while based on estimation, provides a consistent, repeatable, and anatomically plausible framework for deriving the torso bone lengths from the available external measurements.

#### **3.2.4 Shoulders (leftShoulder, rightShoulder)**

The optional leftShoulder and rightShoulder bones in VRM represent the clavicles and are crucial for realistic shoulder deformation. Their length can be derived from the Biacromial Breadth measurement from the AIST database. This measurement represents the total width across the shoulders. A single clavicle does not span this entire distance. A reasonable heuristic is to set the length of a single shoulder bone to **40% of the total biacromial breadth**.

Lshoulder​=Biacromial Breadth×0.40

## **Calculated Bone Proportions for Median Japanese Avatars**

Applying the methodology detailed in the previous section to the median anthropometric data from the AIST 1991-92 survey yields a set of precise bone lengths. These values serve as a production-ready baseline for creating VRM avatars that are proportionally representative of the young-adult Japanese demographic of that era. The results are presented separately for male and female models, reflecting the distinct anthropometric differences between the sexes. All lengths are provided in meters to ensure direct compliance with the VRM specification.

### **4.1 Bone Lengths for Median Young-Adult Japanese Male**

The following table details the calculated bone lengths for a VRM avatar based on the median measurements of a young-adult Japanese male with a stature of 1.714 meters (approx. 5' 7.5").

| VRM Bone Name    | Parent Bone   | Calculated Length (m)           |
| :--------------- | :------------ | :------------------------------ |
| **Torso & Head** |               |                                 |
| hips             | _(Root)_      | _(Positional, length is 0\)_    |
| spine            | hips          | 0.217                           |
| chest            | spine         | 0.217                           |
| upperChest       | chest         | 0.217                           |
| neck             | upperChest    | 0.105                           |
| head             | neck          | 0.157                           |
| **Left Leg**     |               |                                 |
| leftUpperLeg     | hips          | 0.403                           |
| leftLowerLeg     | leftUpperLeg  | 0.334                           |
| leftFoot         | leftLowerLeg  | _(Length depends on foot mesh)_ |
| **Right Leg**    |               |                                 |
| rightUpperLeg    | hips          | 0.403                           |
| rightLowerLeg    | rightUpperLeg | 0.334                           |
| rightFoot        | rightLowerLeg | _(Length depends on foot mesh)_ |
| **Left Arm**     |               |                                 |
| leftShoulder     | upperChest    | 0.156                           |
| leftUpperArm     | leftShoulder  | 0.292                           |
| leftLowerArm     | leftUpperArm  | 0.292                           |
| leftHand         | leftLowerArm  | _(Length depends on hand mesh)_ |
| **Right Arm**    |               |                                 |
| rightShoulder    | upperChest    | 0.156                           |
| rightUpperArm    | rightShoulder | 0.292                           |
| rightLowerArm    | rightUpperArm | 0.292                           |
| rightHand        | rightLowerArm | _(Length depends on hand mesh)_ |

### **4.2 Bone Lengths for Median Young-Adult Japanese Female**

The following table details the calculated bone lengths for a VRM avatar based on the median measurements of a young-adult Japanese female with a stature of 1.594 meters (approx. 5' 2.8").

| VRM Bone Name    | Parent Bone   | Calculated Length (m)           |
| :--------------- | :------------ | :------------------------------ |
| **Torso & Head** |               |                                 |
| hips             | _(Root)_      | _(Positional, length is 0\)_    |
| spine            | hips          | 0.205                           |
| chest            | spine         | 0.205                           |
| upperChest       | chest         | 0.205                           |
| neck             | upperChest    | 0.098                           |
| head             | neck          | 0.146                           |
| **Left Leg**     |               |                                 |
| leftUpperLeg     | hips          | 0.370                           |
| leftLowerLeg     | leftUpperLeg  | 0.307                           |
| leftFoot         | leftLowerLeg  | _(Length depends on foot mesh)_ |
| **Right Leg**    |               |                                 |
| rightUpperLeg    | hips          | 0.370                           |
| rightLowerLeg    | rightUpperLeg | 0.307                           |
| rightFoot        | rightLowerLeg | _(Length depends on foot mesh)_ |
| **Left Arm**     |               |                                 |
| leftShoulder     | upperChest    | 0.142                           |
| leftUpperArm     | leftShoulder  | 0.272                           |
| leftLowerArm     | leftUpperArm  | 0.272                           |
| leftHand         | leftLowerArm  | _(Length depends on hand mesh)_ |
| **Right Arm**    |               |                                 |
| rightShoulder    | upperChest    | 0.142                           |
| rightUpperArm    | rightShoulder | 0.272                           |
| rightLowerArm    | rightUpperArm | 0.272                           |
| rightHand        | rightLowerArm | _(Length depends on hand mesh)_ |

## **Guidelines for Application in Real-Time Environments**

The calculated bone lengths provide a precise skeletal foundation, but their practical implementation in a real-time 3D environment, such as a game engine or VR platform, requires further consideration. This section provides actionable guidelines for two key areas of application: the creation of physics collision volumes using tapered capsules and the design of a user interface (UI) for realistic character customization.

### **5.1 Tapered Capsule Physics Colliders**

For realistic physical interaction, such as preventing hair or clothing from passing through the body, the avatar's skeleton must be outfitted with a set of physics colliders. The user query specifically requested the use of **tapered capsules**, which are an excellent choice for representing organic forms like limbs and torsos. A standard capsule is a cylinder with two hemispherical ends of the same radius. A tapered capsule, as defined in physics engines like Unreal Engine, is a more advanced primitive defined by a central line segment and two potentially different radii for the capping spheres at each end (Radius0 and Radius1).24 This allows the collider to more accurately match the natural taper of a human limb, which is typically thicker at the proximal end (e.g., the shoulder) and thinner at the distal end (e.g., the elbow).

The Length of each tapered capsule collider should correspond directly to the calculated bone length from the tables in Section 4\. The capsule should be oriented to align with its corresponding bone. However, the source anthropometric data provides no information on body circumference, width, or depth, which are necessary to determine the radii of the colliders. This represents a critical data gap that must be bridged with a robust and configurable heuristic to be of practical use.

A simple and effective method is to derive the radii as a proportion of the bone's length. This ensures that the colliders scale plausibly with the skeleton; longer limbs will be appropriately thicker. The following heuristic is proposed as a starting point for generating tapered capsule radii:

1. Calculate a Base Radius: The primary radius is determined as a fraction of the bone's length. A ratio of 0.25 is a good starting point, but this can be adjusted to create leaner or heavier body types.  
   Rbase​=Lbone​×0.25
2. Apply a Taper Factor: A taper factor determines how much thinner the distal end of the collider is compared to the proximal end. A factor of 0.8 means the distal radius will be 80% of the proximal radius.  
   R0​=Rbase​ (Proximal end, closer to the body's core)  
   R1​=Rbase​×taperFactor (Distal end)

**Example Implementation for a Male leftUpperArm:**

- From Table 4.1, LleftUpperArm​=0.292 m.
- Rbase​=0.292 m×0.25=0.073 m.
- Using a taperFactor of 0.8:
  - R0​ (shoulder radius) \= 0.073 m.
  - R1​ (elbow radius) \= 0.073 m×0.8=0.058 m.

This heuristic provides a logical, data-driven starting point for creating physically plausible colliders. These values can then be exposed to artists or designers as parameters for fine-tuning the final body shape.

### **5.2 UI Design for Character Customization**

The provided anthropometric data, including both mean values and standard deviations, is not only useful for creating a single median avatar but also for designing a character customization system that allows users to create variations within a realistic and demographically-appropriate range.

#### **5.2.1 Categorical and Numeric Sliders**

A user-friendly customization interface can be built using a combination of categorical and numeric sliders.

- **Categorical "Preset" Slider:** A simple dropdown or selector could allow a user to choose a starting point, such as "Median Male" or "Median Female." Selecting one of these options would instantly apply the full set of bone lengths from Table 4.1 or 4.2, respectively.
- **Numeric Proportional Sliders:** For more granular control, numeric sliders can be provided for key body proportions. Instead of allowing users to set absolute bone lengths, which can be unintuitive, it is more effective to provide sliders for relative proportions, such as "Stature," "Leg-to-Body Ratio," and "Arm-to-Body Ratio."

The power of using a statistical dataset like AIST's comes from its ability to define the valid operational range for these sliders. A common practice in statistics is to define a normal range as the mean plus or minus two standard deviations ($ \\mu \\pm 2\\sigma $), as this interval captures approximately 95% of the population distribution. This prevents users from creating anatomically impossible or extreme characters while still allowing for significant variation.

**Example Implementation for a "Stature" Slider (Male):**

- **Data from Table 2.1:** Mean Stature \= 1.714 m, SD \= 0.055 m.
- **Slider Default Value:** 1.714 m.
- **Slider Minimum Value:** 1.714−(2×0.055)=1.604 m.
- **Slider Maximum Value:** 1.714+(2×0.055)=1.824 m.

When the user adjusts this primary "Stature" slider, all other bone lengths would scale proportionally from their base values to maintain the overall body shape. Sliders for "Leg-to-Body Ratio" could then adjust the Crotch Height relative to the Stature, with all subsequent bone length calculations updating in real-time.

#### **5.2.2 Box-and-Whisker Plot Visualization**

To provide users with valuable context for their customizations, a box-and-whisker plot can be displayed alongside each numeric slider. This statistical visualization offers an intuitive graphical representation of where a user's custom selection falls within the real-world population distribution.

The full AIST dataset includes percentile values, which are ideal for constructing these plots. The implementation would be as follows:

- **The Box:** Represents the Interquartile Range (IQR), spanning from the 25th percentile to the 75th percentile. The middle 50% of the population falls within this range.
- **The Median Line:** A line inside the box marks the 50th percentile (the median value).
- **The Whiskers:** Lines extend from the box to show the broader range of common variation, typically representing the 5th and 95th percentiles.
- **User Marker:** A distinct marker or dot is overlaid on the plot to indicate the user's current slider value.

By integrating this visualization, the character creator becomes more than just an aesthetic tool. It allows users to see if they are creating a character with "average" height, "tall but common" legs, or "exceptionally short" arms, all grounded in real-world data. This provides a powerful feedback mechanism for users aiming to create either a realistic self-representation or a deliberately stylized but still plausible character.

## **Conclusions and Recommendations**

This report has successfully established a comprehensive, data-driven framework for generating realistic VRM avatar bone proportions based on the anthropometry of the young-adult Japanese population. By integrating the strict technical requirements of the VRM 1.0 standard with the detailed measurements from the AIST 1991-92 Human Dimension Database, a complete, actionable set of bone lengths has been calculated for both median male and female avatars.

The core contribution of this work lies in its transparent and repeatable methodology. The process of deriving primary body segments from raw anthropometric data and subsequently subdividing them using established anatomical and forensic ratios provides a clear blueprint for translating real-world human data into functional digital skeletons. This methodology is not limited to the specific dataset used; it can be readily applied to other anthropometric surveys for different demographics, provided the necessary segmental measurements are available.

Furthermore, this report extends beyond theoretical calculation to provide practical guidelines for implementation in real-time applications. The proposed heuristics for generating tapered capsule physics colliders and for designing a statistically-informed character customization UI address key production challenges. By defining slider ranges based on the mean and standard deviation of the source population, developers can offer users meaningful customization that is bounded by realism. The recommendation to use box-and-whisker plots as a visual aid provides an innovative way to contextualize user choices against real-world population data, enhancing the user experience.

**Key Recommendations for Developers:**

1. **Adopt the Median Values as a Baseline:** The calculated bone lengths in Tables 4.1 and 4.2 should be used as the default proportions for standard male and female Japanese avatars in VRM-based applications. This will ensure a high degree of anatomical plausibility and consistency.
2. **Implement Heuristics for Physics and Customization:** The proposed methods for calculating tapered capsule radii and for defining UI slider ranges should be implemented as starting points. These parameters should be exposed to technical artists and designers for fine-tuning to match the specific artistic style and performance requirements of the application.
3. **Acknowledge Data Limitations:** Developers should be aware that the foundational data for this report is from the 1991-92 period. Due to secular trends in growth, the average stature of the contemporary young-adult Japanese population may be slightly taller. While the proportional relationships are likely to remain highly stable, the absolute values may differ by a small margin.

**Future Work:**

The primary limitation of this study is the age of the AIST 1991-92 dataset. The logical next step would be to apply the established methodology to a more recent, and equally granular, dataset. The ideal future data source would be a large-scale 3D body scan survey of the Japanese population. Such data would not only provide updated length measurements but would also offer the circumference and volume data needed to directly calculate collider radii, removing the need for heuristics. As such datasets become more accessible, the framework presented in this report can serve as the foundational methodology for generating even more accurate and contemporary digital representations of human populations.
