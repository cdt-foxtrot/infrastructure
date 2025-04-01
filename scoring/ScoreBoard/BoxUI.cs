using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Graphics;
using Microsoft.Xna.Framework.Input;
using System;

namespace Scoreboard
{
    /// <summary>
    /// All needed UI elements for a single Box.
    /// </summary>
    public class BoxUI
    {

        // Fields:
        private HealthBar m_pHealthBar;
        private string m_sTitle;
        private Vector2 m_v2HealthBarPosition;

        // Properties:
        /// <summary>
        /// Gets/sets the health of the box from the HealthBar instance.
        /// </summary>
        public int Health 
        { 
            get { return m_pHealthBar.Health; }
            set { m_pHealthBar.Health = value; }
        }

        // Constructors:
        /// <summary>
        /// Constructs the UI elements for a single box.
        /// </summary>
        /// <param name="a_pHealthTexture">The texture for the hearts of the box.</param>
        /// <param name="a_v2StartPos">The starting position of the HealthBar.</param>
        /// <param name="a_v2PercentScale">The percent scaling for window resizing.</param>
        /// <param name="a_sTitle">The title of the box in the UI.</param>
        public BoxUI(
            Texture2D a_pFullHeart,
            Texture2D a_pHalfHeart,
            Vector2 a_v2StartPos,
            Vector2 a_v2PercentScale,
            string a_sTitle)
        {
            m_v2HealthBarPosition = a_v2StartPos;
            m_pHealthBar = new HealthBar(a_pFullHeart, a_pHalfHeart, a_v2StartPos, a_v2PercentScale);
            m_sTitle = a_sTitle;
        }

        // Methods:
        /// <summary>
        /// Alters necessary scales for UI elements on window resizing.
        /// </summary>
        /// <param name="a_pGraphics">Graphics devices used to get the viewport.</param>
        public void OnResize(GraphicsDeviceManager a_pGraphics)
        {
            m_pHealthBar.OnResize(a_pGraphics);
        }

        /// <summary>
        /// Renders all UI elements to the game window.
        /// </summary>
        /// <param name="a_pSpriteBatch">SpriteBatch used to render objects.</param>
        public void Draw(SpriteBatch a_pSpriteBatch)
        {
            a_pSpriteBatch.DrawString(
                Resources.Font,                 // Font
                m_sTitle,                       // Text
                new Vector2(m_v2HealthBarPosition.X, m_v2HealthBarPosition.Y - 50),     // Position
                Color.Black,                    // Color tint
                0.0f,                           // Rotation
                Vector2.Zero,                   // Origin
                0.5f,                           // Scale
                SpriteEffects.None,             // SpriteEffects
                0.0f);                          // Z Layer

            // Calling the healtbar's draw method.
            m_pHealthBar.Draw(a_pSpriteBatch);
        }
    }
}
