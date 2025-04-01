using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;
using System.Collections.Generic;

namespace Scoreboard
{
    /// <summary>
    /// Main game object, actually contains base main loop logic.
    /// </summary>
    public class Game1 : Game
    {
        // General MonoGame fields.
        private GraphicsDeviceManager m_pGraphics;
        private SpriteBatch m_pSpriteBatch;

        // Background fields.
        private DynamicBackground m_pBackground;
        private DynamicBackground m_pUI;

        // Box UI fields.
        private List<BoxUI> m_lBoxes = new List<BoxUI>();

        // Test code field -- REMOVE AFTER DONE TESTING --
        private KeyboardState prevKBState;

        // Server connection fields.
        private ScoreboardServer m_pServer;
        private const float SERVER_UPDATE_TIME = 0.25f;
        private float m_fTotalTimer = 0;

        /// <summary>
        /// Default constructor for the Game1 object.
        /// </summary>
        public Game1()
        {
            m_pGraphics = new GraphicsDeviceManager(this);
            Content.RootDirectory = "Content";
            IsMouseVisible = true;

            // Allowing the user to resize the window and
            // subscribing the callback method for window resizing.
            Window.AllowUserResizing = true;
            Window.ClientSizeChanged += OnResize;
        }

        /// <summary>
        /// Initializes necessary variables for the Game1 class.
        /// This excludes anything relying on textures.
        /// </summary>
        protected override void Initialize()
        {
            m_pServer = new ScoreboardServer("http://localhost:5000/");

            base.Initialize();
        }

        /// <summary>
        /// Loads in any content such as textures within this method.
        /// </summary>
        protected override void LoadContent()
        {
            m_pSpriteBatch = new SpriteBatch(GraphicsDevice);

            // Initializing the variables for the background of the UI.
            m_pUI = new DynamicBackground(m_pGraphics.GraphicsDevice, new Vector2(75, 75));
            m_pBackground = new DynamicBackground(m_pGraphics.GraphicsDevice, Content);

            Vector2 v2HealthBarPercents = new Vector2(0.01875f, 0.0325f);

            // Loading the individual box health UIs.
            for (int i = 0; i < 10; i++)
            {
                m_lBoxes.Add(new BoxUI(
                    Content.Load<Texture2D>("Minercraft_Heart"),
                    Content.Load<Texture2D>("Minecraft_Half_Heart"),
                    new Vector2(120, 150 + (i * 85.0f)),
                    v2HealthBarPercents,
                    $"Box {i + 1}:"));
            }

            Resources.Font = Content.Load<SpriteFont>("PixelFont");
        }

        /// <summary>
        /// Called every frame, updates logic within the scoreboard.
        /// </summary>
        /// <param name="a_pGameTime">Fundamentally, tracks the change in time between frames.</param>
        protected override async void Update(GameTime a_pGameTime)
        {
            // Creating a delta time variable with GameTime
            float fDeltaTime = (float)a_pGameTime.ElapsedGameTime.TotalSeconds;

            // Setting the keybinds for closing the window.
            if (GamePad.GetState(PlayerIndex.One).Buttons.Back == ButtonState.Pressed || 
                Keyboard.GetState().IsKeyDown(Keys.Escape))
            {
                Exit();
            }

            // -----------------------------------------------------------------------
            //            TEST CODE FOR THE HEALTH DYNAMICALLY CHANGING.
            KeyboardState kbState = Keyboard.GetState();
            if (kbState.IsKeyDown(Keys.Up) && prevKBState.IsKeyUp(Keys.Up))
            {
                m_lBoxes[0].Health += 1;
            }
            if (kbState.IsKeyDown(Keys.Down) && prevKBState.IsKeyUp(Keys.Down))
            {
                m_lBoxes[0].Health -= 1;
            }
            prevKBState = kbState;
            // -----------------------------------------------------------------------

            // Calculating the time for the next update from the server.
            m_fTotalTimer += fDeltaTime;
            if (m_fTotalTimer >= SERVER_UPDATE_TIME)
            {
                // Getting new data from the server.
                await m_pServer.Get();

                // Resetting the timer.
                m_fTotalTimer = 0.0f;
            }

            base.Update(a_pGameTime);
        }

        /// <summary>
        /// Called every frame, renders everything to the Game1 window.
        /// </summary>
        /// <param name="a_pGameTime">Fundamentally, tracks the change in time between frames.</param>
        protected override void Draw(GameTime a_pGameTime)
        {
            // Clearing everything from the window.
            GraphicsDevice.Clear(Color.CornflowerBlue);

            // Beginning the batch rendering.
            m_pSpriteBatch.Begin();

            // Drawing UI elements (painter's algo accounted for).
            m_pBackground.Draw(m_pSpriteBatch);
            m_pUI.Draw(m_pSpriteBatch);

            // Rendering the box health displays.
            for (int i = 0; i < m_lBoxes.Count; i++)
            {
                m_lBoxes[i].Draw(m_pSpriteBatch);
            }

            // Rendering all calls to the window.
            m_pSpriteBatch.End();

            base.Draw(a_pGameTime);
        }


        /// <summary>
        /// Callback method for when the window is resized.
        /// </summary>
        private void OnResize(Object sender, EventArgs e)
        {
            // Applying changes to the viewport if the window has changed dimensions.
            if ((m_pGraphics.PreferredBackBufferWidth != m_pGraphics.GraphicsDevice.Viewport.Width) ||
                (m_pGraphics.PreferredBackBufferHeight != m_pGraphics.GraphicsDevice.Viewport.Height))
            {
                // Setting the actual bounds for the window itself.
                m_pGraphics.PreferredBackBufferWidth = m_pGraphics.GraphicsDevice.Viewport.Width;
                m_pGraphics.PreferredBackBufferHeight = m_pGraphics.GraphicsDevice.Viewport.Height;
                m_pGraphics.ApplyChanges();

                // Calling all necessary resizing functionalities:
                m_pBackground.OnResize(m_pGraphics);
                m_pUI.OnResize(m_pGraphics);
                for (int i = 0; i < m_lBoxes.Count; i++)
                {
                    m_lBoxes[i].OnResize(m_pGraphics);
                }
            }
        }
    }
}
